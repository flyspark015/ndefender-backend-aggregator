"""RemoteID JSONL ingestion."""

from __future__ import annotations

import asyncio
import json
import time
from contextlib import suppress

from ..bus import EventBus
from ..config import AppConfig
from ..contacts import ContactStore
from ..ingest import Ingestor, IngestorMetadata
from ..models import EventEnvelope
from ..state import StateStore
from .jsonl_tail import JsonlTailer


class RemoteIdIngestor(Ingestor):
    """Tail RemoteID JSONL and normalize events."""

    metadata = IngestorMetadata(name="remoteid", source="remoteid")

    def __init__(
        self,
        config: AppConfig,
        state_store: StateStore,
        event_bus: EventBus,
        contact_store: ContactStore | None = None,
    ) -> None:
        self._config = config
        self._state_store = state_store
        self._event_bus = event_bus
        self._contact_store = contact_store
        self._tailer = JsonlTailer(
            config.remoteid.jsonl_path,
            config.remoteid.tail_poll_interval_ms,
        )
        self._task: asyncio.Task[None] | None = None
        self._watchdog: asyncio.Task[None] | None = None
        self._running = False
        self._last_error: str | None = None
        self._last_event_ms: int | None = None

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run())
        self._watchdog = asyncio.create_task(self._monitor_staleness())

    async def stop(self) -> None:
        if not self._running:
            return
        self._running = False
        if self._task:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task
        if self._watchdog:
            self._watchdog.cancel()
            with suppress(asyncio.CancelledError):
                await self._watchdog

    async def health(self) -> dict[str, str]:
        status = "ok" if self._running else "stopped"
        payload = {"status": status, "running": str(self._running).lower()}
        if self._last_error:
            payload["last_error"] = self._last_error
        return payload

    async def handle_event(self, event: EventEnvelope) -> None:
        return None

    async def _run(self) -> None:
        async for line in self._tailer.tail():
            if not self._running:
                break
            try:
                await self._process_line(line)
            except Exception as exc:
                self._last_error = str(exc)
                await self._state_store.update_section(
                    "remote_id",
                    {
                        "state": "DEGRADED",
                        "capture_active": False,
                        "last_error": self._last_error,
                    },
                )

    async def _process_line(self, line: str) -> None:
        payload = json.loads(line)
        if not isinstance(payload, dict):
            return
        event_type = payload.get("type")
        timestamp_raw = payload.get("timestamp") or payload.get("timestamp_ms") or time.time() * 1000
        timestamp_ms = self._normalize_ts(timestamp_raw)
        data = payload.get("data") or {}

        if self._contact_store:
            replay_active = await self._contact_store.replay_active()
            if not replay_active and self._is_stale(timestamp_ms):
                return
            if not replay_active and self._is_test_contact(data):
                return

        self._last_event_ms = timestamp_ms
        remote_state = data.get("state") or data.get("status")
        remote_mode = data.get("mode")
        remote_last_ts = data.get("last_ts") or data.get("last_timestamp_ms")
        await self._state_store.update_section(
            "remote_id",
            {
                "last_event_type": event_type,
                "last_event": data,
                "last_timestamp_ms": timestamp_ms,
                "state": remote_state,
                "mode": remote_mode or "live",
                "capture_active": data.get("capture_active"),
                "last_ts": remote_last_ts,
            },
        )
        if self._contact_store and event_type:
            event_name = str(event_type)
            if event_name in {"CONTACT_NEW", "CONTACT_UPDATE", "CONTACT_LOST"}:
                await self._contact_store.update_remoteid(event_name, data, timestamp_ms)
            if event_name == "REPLAY_STATE":
                await self._contact_store.update_replay(data)

        envelope = EventEnvelope(
            type=str(event_type) if event_type else "TELEMETRY_UPDATE",
            timestamp_ms=timestamp_ms,
            source="remoteid",
            data=data,
        )
        await self._event_bus.publish(envelope)

    async def _monitor_staleness(self) -> None:
        while self._running:
            await asyncio.sleep(5)
            if not self._running:
                break
            if self._contact_store and await self._contact_store.replay_active():
                continue
            if not self._last_event_ms:
                await self._state_store.update_section(
                    "remote_id",
                    {
                        "state": "DEGRADED",
                        "capture_active": False,
                        "last_error": "no_remoteid_events",
                    },
                )
                continue
            if self._is_stale(self._last_event_ms):
                await self._state_store.update_section(
                    "remote_id",
                    {
                        "state": "DEGRADED",
                        "capture_active": False,
                        "last_error": "remoteid_stale",
                        "last_timestamp_ms": self._last_event_ms,
                    },
                )

    @staticmethod
    def _normalize_ts(value: object) -> int:
        try:
            ts = int(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return int(time.time() * 1000)
        if ts < 100000000000:
            return ts * 1000
        return ts

    @staticmethod
    def _is_stale(timestamp_ms: int, ttl_ms: int = 15000) -> bool:
        return int(time.time() * 1000) - timestamp_ms > ttl_ms

    @staticmethod
    def _is_test_contact(data: dict[str, object]) -> bool:
        markers = ("testdrone", "warmstart")
        for value in data.values():
            if isinstance(value, str):
                lowered = value.lower()
                if any(marker in lowered for marker in markers):
                    return True
        return False
