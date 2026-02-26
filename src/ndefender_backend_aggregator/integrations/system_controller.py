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
from .ups_hat_e import UpsHatEReader


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
        self._ups_reader = UpsHatEReader()
        self._last_ups_error: str | None = None

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
                await self._mark_offline(self._last_error)
            await asyncio.sleep(interval_s)

    async def _poll_status(self) -> None:
        if not self._client:
            return
        response = await self._client.get("/api/v1/status")
        response.raise_for_status()
        payload = response.json() or {}
        await self._state_store.update_section("system", payload.get("system") or {})
        power_payload = payload.get("power") or payload.get("ups") or {}
        if not self._power_has_data(power_payload):
            local_ups = await self._read_local_ups()
            if local_ups:
                power_payload = local_ups
            elif not power_payload:
                power_payload = {"status": "offline", "last_error": self._last_ups_error or "ups_unavailable"}
        await self._state_store.update_section("power", power_payload)
        await self._state_store.update_section("services", payload.get("services") or [])
        await self._state_store.update_section("network", payload.get("network") or {})
        await self._state_store.update_section("gps", payload.get("gps") or {})
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

    async def _mark_offline(self, error: str) -> None:
        offline = {"status": "offline", "last_error": error}
        await self._state_store.update_section("system", offline)
        power_payload = await self._read_local_ups()
        if power_payload is None:
            power_payload = {"status": "offline", "last_error": self._last_ups_error or error}
        await self._state_store.update_section("power", power_payload)
        await self._state_store.update_section("network", {"connected": False})
        await self._state_store.update_section(
            "gps",
            {
                "timestamp_ms": int(time.time() * 1000),
                "fix": "NO_FIX",
                "last_error": error,
            },
        )
        await self._state_store.update_section("audio", offline)

    def _power_has_data(self, payload: dict[str, object]) -> bool:
        for key in ("pack_voltage_v", "current_a", "input_vbus_v", "input_power_w", "soc_percent"):
            if payload.get(key) is not None:
                return True
        return False

    async def _read_local_ups(self) -> dict[str, object] | None:
        if not self._ups_reader:
            return None
        data = await asyncio.to_thread(self._ups_reader.read_status)
        if data:
            self._last_ups_error = None
            return data
        self._last_ups_error = self._ups_reader.last_error or "ups_read_failed"
        return None
