"""System Controller integration."""

from __future__ import annotations

import asyncio
import time
from contextlib import suppress

import httpx

from ..bus import EventBus
from ..config import AppConfig
from ..ingest import Ingestor, IngestorMetadata
from ..models import EventEnvelope
from ..state import StateStore


class SystemControllerIngestor(Ingestor):
    """Poll System Controller and update state."""

    metadata = IngestorMetadata(name="system-controller", source="system")

    def __init__(self, config: AppConfig, state_store: StateStore, event_bus: EventBus) -> None:
        self._config = config
        self._state_store = state_store
        self._event_bus = event_bus
        self._client: httpx.AsyncClient | None = None
        self._task: asyncio.Task[None] | None = None
        self._running = False
        self._last_success_ms: int | None = None
        self._last_error: str | None = None

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._client = httpx.AsyncClient(
            base_url=self._config.system_controller.base_url,
            timeout=self._config.system_controller.timeout_seconds,
        )
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if not self._running:
            return
        self._running = False
        if self._task:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task
        if self._client:
            await self._client.aclose()
            self._client = None

    async def health(self) -> dict[str, str]:
        status = "ok" if self._last_success_ms else "degraded"
        if not self._running:
            status = "stopped"
        payload = {"status": status, "running": str(self._running).lower()}
        if self._last_success_ms:
            payload["last_success_ms"] = str(self._last_success_ms)
        if self._last_error:
            payload["last_error"] = self._last_error
        return payload

    async def handle_event(self, event: EventEnvelope) -> None:
        return None

    async def _run(self) -> None:
        interval_s = self._config.polling.system_controller_interval_ms / 1000
        while self._running:
            try:
                await self._poll_status()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                self._last_error = str(exc)
            await asyncio.sleep(interval_s)

    async def _poll_status(self) -> None:
        if not self._client:
            return
        headers = {}
        if self._config.system_controller.api_key:
            headers["X-API-Key"] = self._config.system_controller.api_key
        response = await self._client.get("/api/v1/status", headers=headers)
        response.raise_for_status()
        payload = response.json() or {}
        await self._state_store.update_section("system", payload.get("system") or {})
        await self._state_store.update_section("power", payload.get("ups") or {})
        await self._state_store.update_section("services", payload.get("services") or [])
        await self._state_store.update_section("network", payload.get("network") or {})
        await self._state_store.update_section("audio", payload.get("audio") or {})

        now_ms = int(time.time() * 1000)
        self._last_success_ms = now_ms
        self._last_error = None
        envelope = EventEnvelope(
            type="SYSTEM_UPDATE",
            timestamp_ms=payload.get("timestamp_ms", now_ms),
            source="system",
            data=payload,
        )
        await self._event_bus.publish(envelope)
