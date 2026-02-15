"""ESP32 serial integration."""

from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from collections.abc import Callable
from contextlib import suppress
from pathlib import Path
from typing import Any

import serial

from ..bus import EventBus
from ..commands.contracts import CommandResult
from ..config import AppConfig
from ..ingest import Ingestor, IngestorMetadata
from ..models import EventEnvelope
from ..state import StateStore

LOGGER = logging.getLogger(__name__)


class Esp32Ingestor(Ingestor):
    """ESP32 serial ingestion with command routing."""

    metadata = IngestorMetadata(name="esp32", source="esp32")

    def __init__(
        self,
        config: AppConfig,
        state_store: StateStore,
        event_bus: EventBus,
        serial_factory: Callable[..., serial.Serial] | None = None,
    ) -> None:
        self._config = config
        self._state_store = state_store
        self._event_bus = event_bus
        self._serial_factory = serial_factory or serial.Serial
        self._serial: serial.Serial | None = None
        self._buffer = bytearray()
        self._pending: dict[str, asyncio.Future[dict[str, Any]]] = {}
        self._write_lock = asyncio.Lock()
        self._task: asyncio.Task[None] | None = None
        self._running = False
        self._connected = False
        self._last_telemetry_ms: int | None = None
        self._last_error: str | None = None

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if not self._running:
            return
        self._running = False
        if self._task:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task
        await self._close_serial()

    async def health(self) -> dict[str, str]:
        status = "ok" if self._connected else "degraded"
        if not self._running:
            status = "stopped"
        payload = {"status": status, "running": str(self._running).lower()}
        if self._last_telemetry_ms:
            payload["last_telemetry_ms"] = str(self._last_telemetry_ms)
        if self._last_error:
            payload["last_error"] = self._last_error
        return payload

    async def handle_event(self, event: EventEnvelope) -> None:
        return None

    async def send_command(self, cmd: str, args: dict[str, Any]) -> CommandResult:
        if not self._connected or not self._serial:
            result = CommandResult(
                command=cmd,
                command_id=str(uuid.uuid4()),
                accepted=False,
                detail="serial not connected",
                timestamp_ms=int(time.time() * 1000),
            )
            await self._publish_command_ack(result, ok=False, err="serial_not_connected")
            return result

        timeout_s = self._config.esp32.command_timeout_seconds
        retries = self._config.esp32.command_retries
        last_error = "timeout"

        for _ in range(retries + 1):
            command_id = str(uuid.uuid4())
            future: asyncio.Future[dict[str, Any]] = asyncio.get_running_loop().create_future()
            self._pending[command_id] = future
            payload = {"id": command_id, "cmd": cmd, "args": args or {}}
            await self._write_json(payload)
            try:
                ack = await asyncio.wait_for(future, timeout=timeout_s)
                ok = bool(ack.get("ok", False))
                err = ack.get("err")
                return CommandResult(
                    command=cmd,
                    command_id=command_id,
                    accepted=ok,
                    detail=err,
                    timestamp_ms=int(time.time() * 1000),
                )
            except TimeoutError:
                last_error = "timeout"
            finally:
                self._pending.pop(command_id, None)

        result = CommandResult(
            command=cmd,
            command_id=str(uuid.uuid4()),
            accepted=False,
            detail=last_error,
            timestamp_ms=int(time.time() * 1000),
        )
        await self._publish_command_ack(result, ok=False, err=last_error)
        return result

    async def _publish_command_ack(self, result: CommandResult, ok: bool, err: str | None) -> None:
        envelope = EventEnvelope(
            type="COMMAND_ACK",
            timestamp_ms=result.timestamp_ms,
            source="esp32",
            data={
                "id": result.command_id,
                "ok": ok,
                "err": err,
                "data": {"cmd": result.command},
            },
        )
        await self._event_bus.publish(envelope)

    async def _run(self) -> None:
        while self._running:
            if not self._serial:
                port = self._resolve_port()
                if not port:
                    await asyncio.sleep(self._config.esp32.reconnect_delay_seconds)
                    continue
                try:
                    await asyncio.to_thread(self._open_serial, port)
                    self._connected = True
                    LOGGER.info("ESP32 connected on %s", port)
                except Exception as exc:
                    self._last_error = str(exc)
                    await asyncio.sleep(self._config.esp32.reconnect_delay_seconds)
                    continue
            try:
                await self._read_once()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                self._last_error = str(exc)
                await self._close_serial()
                await asyncio.sleep(self._config.esp32.reconnect_delay_seconds)

    async def _read_once(self) -> None:
        if not self._serial:
            return
        chunk_size = self._config.esp32.read_chunk_bytes
        data = await asyncio.to_thread(self._serial.read, chunk_size)
        if not data:
            return
        self._buffer.extend(data)
        if len(self._buffer) > self._config.esp32.max_line_bytes:
            self._buffer.clear()
            return
        while b"\n" in self._buffer:
            line, _, rest = self._buffer.partition(b"\n")
            self._buffer = bytearray(rest)
            await self._process_line(line)

    async def _process_line(self, line: bytes) -> None:
        text = line.decode("utf-8", errors="ignore").strip()
        if not text:
            return
        if len(text) > self._config.esp32.max_line_bytes:
            return
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            return
        if not isinstance(payload, dict):
            return
        await self._handle_message(payload)

    async def _handle_message(self, payload: dict[str, Any]) -> None:
        msg_type = payload.get("type")
        timestamp_ms = int(payload.get("timestamp_ms") or time.time() * 1000)
        if msg_type == "telemetry":
            await self._state_store.update_section(
                "vrx",
                {
                    "selected": payload.get("sel"),
                    "vrx": payload.get("vrx", []),
                    "led": payload.get("led", {}),
                    "sys": payload.get("sys", {}),
                },
            )
            await self._state_store.update_section("video", payload.get("video", {}))
            self._last_telemetry_ms = timestamp_ms
            await self._event_bus.publish(
                EventEnvelope(
                    type="ESP32_TELEMETRY",
                    timestamp_ms=timestamp_ms,
                    source="esp32",
                    data=payload,
                )
            )
            return
        if msg_type == "command_ack":
            ack_id = payload.get("id")
            if ack_id and ack_id in self._pending:
                future = self._pending.get(ack_id)
                if future and not future.done():
                    future.set_result(payload)
            await self._event_bus.publish(
                EventEnvelope(
                    type="COMMAND_ACK",
                    timestamp_ms=timestamp_ms,
                    source="esp32",
                    data=payload,
                )
            )
            return
        if msg_type == "log_event":
            await self._event_bus.publish(
                EventEnvelope(
                    type="LOG_EVENT",
                    timestamp_ms=timestamp_ms,
                    source="esp32",
                    data=payload,
                )
            )

    def _resolve_port(self) -> str | None:
        serial_by_id = Path("/dev/serial/by-id")
        if serial_by_id.exists():
            entries = sorted(serial_by_id.glob("*"))
            if entries:
                return str(entries[0])
        return self._config.esp32.serial_port

    def _open_serial(self, port: str) -> None:
        self._serial = self._serial_factory(
            port,
            baudrate=self._config.esp32.baud_rate,
            timeout=0.2,
        )

    async def _close_serial(self) -> None:
        if self._serial:
            await asyncio.to_thread(self._serial.close)
        self._serial = None
        self._connected = False

    async def _write_json(self, payload: dict[str, Any]) -> None:
        if not self._serial:
            return
        data = (json.dumps(payload, separators=(",", ":")) + "\n").encode("utf-8")
        async with self._write_lock:
            await asyncio.to_thread(self._serial.write, data)
