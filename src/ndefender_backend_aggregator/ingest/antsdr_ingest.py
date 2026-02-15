"""AntSDR JSONL ingestion."""

from __future__ import annotations

import asyncio
import json
import time
from contextlib import suppress
from typing import Any

from ..bus import EventBus
from ..config import AppConfig
from ..ingest import Ingestor, IngestorMetadata
from ..models import EventEnvelope
from ..state import StateStore
from .jsonl_tail import JsonlTailer


class AntsdrIngestor(Ingestor):
    """Tail AntSDR JSONL and normalize events."""

    metadata = IngestorMetadata(name="antsdr", source="antsdr")

    def __init__(self, config: AppConfig, state_store: StateStore, event_bus: EventBus) -> None:
        self._config = config
        self._state_store = state_store
        self._event_bus = event_bus
        self._tailer = JsonlTailer(
            config.antsdr.jsonl_path,
            config.antsdr.tail_poll_interval_ms,
        )
        self._task: asyncio.Task[None] | None = None
        self._running = False
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
        timestamp_ms = int(
            payload.get("timestamp") or payload.get("timestamp_ms") or time.time() * 1000
        )
        data = payload.get("data") or {}
        await self._state_store.update_section(
            "rf",
            {"last_event_type": event_type, "last_event": data, "last_timestamp_ms": timestamp_ms},
        )
        envelope = EventEnvelope(
            type=self._normalize_type(event_type),
            timestamp_ms=timestamp_ms,
            source="antsdr",
            data=data,
        )
        await self._event_bus.publish(envelope)

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
