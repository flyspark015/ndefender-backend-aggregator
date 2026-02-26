"""AntSDR JSONL ingestion."""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
import time
from contextlib import suppress
from pathlib import Path
from typing import Any

import yaml

from ..bus import EventBus
from ..config import AppConfig
from ..contacts import ContactStore
from ..ingest import Ingestor, IngestorMetadata
from ..models import EventEnvelope
from ..state import StateStore
from .jsonl_tail import JsonlTailer


class AntsdrIngestor(Ingestor):
    """Tail AntSDR JSONL and normalize events."""

    metadata = IngestorMetadata(name="antsdr", source="antsdr")

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
            config.antsdr.jsonl_path,
            config.antsdr.tail_poll_interval_ms,
        )
        self._task: asyncio.Task[None] | None = None
        self._watchdog: asyncio.Task[None] | None = None
        self._running = False
        self._last_error: str | None = None
        self._last_event_ms: int | None = None
        self._last_health_check_ms: int | None = None
        self._cached_reachable: bool | None = None

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

    async def _process_line(self, line: str) -> None:
        payload = json.loads(line)
        if not isinstance(payload, dict):
            return
        event_type = payload.get("type")
        raw_ts = (
            payload.get("ts_ms")
            or payload.get("timestamp_ms")
            or payload.get("timestamp")
            or time.time() * 1000
        )
        try:
            timestamp_ms = int(raw_ts)
        except (TypeError, ValueError):
            timestamp_ms = int(time.time() * 1000)
        if timestamp_ms < 100000000000:
            timestamp_ms *= 1000
        data = payload.get("data") or {}
        self._last_event_ms = timestamp_ms
        await self._state_store.update_section(
            "rf",
            {
                "last_event_type": event_type,
                "last_event": data,
                "last_timestamp_ms": timestamp_ms,
                "scan_active": True,
                "status": "ok",
                "last_error": None,
            },
        )
        await self._state_store.update_section(
            "antsdr",
            {
                "timestamp_ms": timestamp_ms,
                "connected": True,
                "uri": self._load_antsdr_uri(),
                "temperature_c": data.get("temperature_c"),
                "last_error": None,
            },
        )
        if self._contact_store and event_type:
            await self._contact_store.update_rf(str(event_type), data, timestamp_ms)
        envelope = EventEnvelope(
            type=self._normalize_type(event_type),
            timestamp_ms=timestamp_ms,
            source="antsdr",
            data=data,
        )
        await self._event_bus.publish(envelope)

    async def _monitor_staleness(self) -> None:
        while self._running:
            await asyncio.sleep(5)
            if not self._running:
                break
            now_ms = int(time.time() * 1000)
            if not self._last_event_ms:
                reason = "no_rf_events"
                status = "degraded"
                if not Path(self._config.antsdr.jsonl_path).exists():
                    reason = "rf_jsonl_missing"
                    status = "offline"
                else:
                    reachable = await self._antsdr_reachable()
                    if reachable is False:
                        reason = "antsdr_unreachable"
                        status = "offline"
                await self._state_store.update_section(
                    "rf",
                    {
                        "last_event_type": "RF_SCAN_OFFLINE",
                        "last_event": {"reason": reason},
                        "last_timestamp_ms": now_ms,
                        "scan_active": False,
                        "status": status,
                        "last_error": reason,
                    },
                )
                await self._state_store.update_section(
                    "antsdr",
                    {
                        "timestamp_ms": now_ms,
                        "connected": False,
                        "uri": self._load_antsdr_uri(),
                        "temperature_c": None,
                        "last_error": reason,
                    },
                )
                continue
            if self._is_stale(self._last_event_ms):
                await self._state_store.update_section(
                    "rf",
                    {
                        "last_event_type": "RF_SCAN_STALE",
                        "last_event": {
                            "reason": "no_recent_rf_events",
                            "last_seen_ms": self._last_event_ms,
                        },
                        "last_timestamp_ms": now_ms,
                        "scan_active": False,
                        "status": "degraded",
                        "last_error": "no_recent_rf_events",
                    },
                )
                await self._state_store.update_section(
                    "antsdr",
                    {
                        "timestamp_ms": now_ms,
                        "connected": False,
                        "uri": self._load_antsdr_uri(),
                        "temperature_c": None,
                        "last_error": "no_recent_rf_events",
                    },
                )

    @staticmethod
    def _normalize_type(event_type: Any) -> str:
        mapping = {
            "CONTACT_NEW": "RF_CONTACT_NEW",
            "CONTACT_UPDATE": "RF_CONTACT_UPDATE",
            "CONTACT_LOST": "RF_CONTACT_LOST",
        }
        if not event_type:
            return "RF_CONTACT_UPDATE"
        return mapping.get(str(event_type), str(event_type))

    @staticmethod
    def _is_stale(timestamp_ms: int, ttl_ms: int = 15000) -> bool:
        return int(time.time() * 1000) - timestamp_ms > ttl_ms

    async def _antsdr_reachable(self) -> bool | None:
        now_ms = int(time.time() * 1000)
        if self._last_health_check_ms and (now_ms - self._last_health_check_ms) < 10000:
            return self._cached_reachable

        def _check() -> bool | None:
            uri = self._load_antsdr_uri()
            if not uri:
                return None
            host = self._extract_host(uri)
            if not host:
                return None
            try:
                result = subprocess.run(
                    ["ping", "-c", "1", "-W", "1", host],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=2,
                    check=False,
                )
                return result.returncode == 0
            except Exception:
                return None

        reachable = await asyncio.to_thread(_check)
        self._last_health_check_ms = now_ms
        self._cached_reachable = reachable
        return reachable

    @staticmethod
    def _extract_host(uri: str) -> str | None:
        if uri.startswith("ip:"):
            rest = uri.split(":", 1)[1]
            return rest.split(":")[0]
        return None

    @staticmethod
    def _load_antsdr_uri() -> str | None:
        env_uri = os.getenv("NDEFENDER_ANTSDR_URI")
        if env_uri:
            return env_uri
        for path in (
            Path("/home/toybook/antsdr_scan/config.yaml"),
            Path("/opt/ndefender/antsdr_scan/config.yaml"),
        ):
            if not path.exists():
                continue
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            except Exception:
                continue
            if isinstance(data, dict):
                radio = data.get("radio")
                if isinstance(radio, dict):
                    uri = radio.get("uri")
                    if isinstance(uri, str) and uri:
                        return uri
        return None
