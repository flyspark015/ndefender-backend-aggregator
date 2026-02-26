"""FastAPI entrypoint."""

from __future__ import annotations

import asyncio
import re
import time
import uuid
from contextlib import asynccontextmanager, suppress
from typing import Any

import httpx
from fastapi import Body, Depends, FastAPI, HTTPException, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .bus import EventBus
from .commands import CommandRequest, CommandRouter, Esp32CommandHandler, SystemCommandHandler
from .config import get_config
from .contacts import ContactStore
from .integrations.esp32_serial import Esp32Ingestor
from .logging import configure_logging
from .models import EventEnvelope, StatusSnapshot
from .rate_limit import command_rate_limit, dangerous_rate_limit
from .runtime import build_default_orchestrator
from .state import StateStore
from .ws import WebSocketManager


class CommandAck:
    def __init__(self, command: str, accepted: bool, detail: str | None = None) -> None:
        self.command = command
        self.accepted = accepted
        self.detail = detail
        self.command_id = str(uuid.uuid4())

    def model_dump(self) -> dict[str, Any]:
        payload = {
            "command": self.command,
            "accepted": self.accepted,
            "command_id": self.command_id,
        }
        if self.detail:
            payload["detail"] = self.detail
        return payload


class CommandBody(BaseModel):
    payload: dict[str, Any] = Field(default_factory=dict)
    confirm: bool = False


COMMAND_BODY = Body(default_factory=CommandBody)


def require_confirm(body: CommandBody) -> None:
    if not body.confirm:
        raise HTTPException(status_code=400, detail="confirm_required")


def require_local(request: Request) -> None:
    host = request.client.host if request.client else ""
    if host not in {"127.0.0.1", "::1"}:
        raise HTTPException(status_code=403, detail="local_only")


def _get_client(request: Request, name: str) -> httpx.AsyncClient | None:
    return request.app.state.http_clients.get(name)


async def _proxy_get(client: httpx.AsyncClient, path: str) -> dict[str, Any]:
    response = await client.get(path)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise HTTPException(status_code=500, detail="invalid_response")
    return data


async def _proxy_post(client: httpx.AsyncClient, path: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = await client.post(path, json=payload)
    if response.status_code >= 400:
        detail = "proxy_error"
        try:
            body = response.json()
            if isinstance(body, dict) and "detail" in body:
                detail = str(body.get("detail"))
        except Exception:
            detail = response.text.strip() or detail
        raise HTTPException(status_code=response.status_code, detail=detail)
    data = response.json()
    if not isinstance(data, dict):
        raise HTTPException(status_code=500, detail="invalid_response")
    return data


def _register_read_routes(app: FastAPI, state_store: StateStore) -> None:
    @app.get("/api/v1/health")
    async def health() -> dict[str, Any]:
        return {"status": "ok", "timestamp_ms": int(time.time() * 1000)}

    @app.get("/api/v1/status")
    async def status() -> StatusSnapshot:
        return await state_store.snapshot()

    @app.get("/api/v1/contacts")
    async def contacts() -> dict[str, Any]:
        snapshot = await state_store.snapshot()
        return {"contacts": snapshot.contacts}

    @app.get("/api/v1/system")
    async def system() -> dict[str, Any]:
        snapshot = await state_store.snapshot()
        return snapshot.system

    @app.get("/api/v1/power")
    async def power() -> dict[str, Any]:
        snapshot = await state_store.snapshot()
        return snapshot.power

    @app.get("/api/v1/rf")
    async def rf() -> dict[str, Any]:
        snapshot = await state_store.snapshot()
        return snapshot.rf

    @app.get("/api/v1/video")
    async def video() -> dict[str, Any]:
        snapshot = await state_store.snapshot()
        return snapshot.video

    @app.get("/api/v1/services")
    async def services() -> list[dict[str, Any]]:
        snapshot = await state_store.snapshot()
        return snapshot.services

    @app.get("/api/v1/network")
    async def network() -> dict[str, Any]:
        snapshot = await state_store.snapshot()
        return snapshot.network

    @app.get("/api/v1/gps")
    async def gps() -> dict[str, Any]:
        snapshot = await state_store.snapshot()
        return snapshot.gps

    @app.get("/api/v1/esp32")
    async def esp32() -> dict[str, Any]:
        snapshot = await state_store.snapshot()
        return snapshot.esp32

    @app.get("/api/v1/antsdr")
    async def antsdr() -> dict[str, Any]:
        snapshot = await state_store.snapshot()
        return snapshot.antsdr

    @app.get("/api/v1/audio")
    async def audio() -> dict[str, Any]:
        snapshot = await state_store.snapshot()
        return snapshot.audio


def _register_command_routes(app: FastAPI, config, command_router: CommandRouter) -> None:
    async def dispatch_command(
        command: str,
        body: CommandBody,
        request: Request,
    ) -> dict[str, Any]:
        cmd_request = CommandRequest(
            command=command,
            payload=body.payload,
            confirm=body.confirm,
            issued_by=request.client.host if request.client else None,
        )
        result = await command_router.dispatch(cmd_request)
        if not result.accepted:
            raise HTTPException(status_code=409, detail=result.detail or "invalid_state")
        return result.model_dump()

    @app.post(
        "/api/v1/vrx/tune",
        dependencies=[Depends(command_rate_limit)],
    )
    async def vrx_tune(
        request: Request,
        body: CommandBody = COMMAND_BODY,
    ) -> dict[str, Any]:
        return await dispatch_command("vrx/tune", body, request)

    @app.post(
        "/api/v1/scan/start",
        dependencies=[Depends(command_rate_limit)],
    )
    async def scan_start(
        request: Request,
        body: CommandBody = COMMAND_BODY,
    ) -> dict[str, Any]:
        return await dispatch_command("scan/start", body, request)

    @app.post(
        "/api/v1/scan/stop",
        dependencies=[Depends(command_rate_limit)],
    )
    async def scan_stop(
        request: Request,
        body: CommandBody = COMMAND_BODY,
    ) -> dict[str, Any]:
        return await dispatch_command("scan/stop", body, request)

    @app.post(
        "/api/v1/video/select",
        dependencies=[Depends(command_rate_limit)],
    )
    async def video_select(
        request: Request,
        body: CommandBody = COMMAND_BODY,
    ) -> dict[str, Any]:
        return await dispatch_command("video/select", body, request)

    @app.post("/api/v1/system/reboot")
    async def system_reboot(
        request: Request,
        body: CommandBody = COMMAND_BODY,
    ) -> dict[str, Any]:
        require_confirm(body)
        await command_rate_limit(request)
        await dangerous_rate_limit(request)
        if not config.safety.allow_unsafe_operations:
            raise HTTPException(status_code=403, detail="unsafe_disabled")
        return await dispatch_command("system/reboot", body, request)

    @app.post("/api/v1/system/shutdown")
    async def system_shutdown(
        request: Request,
        body: CommandBody = COMMAND_BODY,
    ) -> dict[str, Any]:
        require_confirm(body)
        await command_rate_limit(request)
        await dangerous_rate_limit(request)
        if not config.safety.allow_unsafe_operations:
            raise HTTPException(status_code=403, detail="unsafe_disabled")
        return await dispatch_command("system/shutdown", body, request)


def _register_proxy_routes(app: FastAPI, state_store: StateStore) -> None:
    @app.get("/api/v1/network/wifi/state")
    async def wifi_state(request: Request) -> dict[str, Any]:
        client = _get_client(request, "system")
        now_ms = int(time.time() * 1000)
        if not client:
            return {
                "timestamp_ms": now_ms,
                "enabled": None,
                "connected": False,
                "ssid": None,
                "bssid": None,
                "ip": None,
                "rssi_dbm": None,
                "link_quality": None,
                "last_update_ms": now_ms,
                "last_error": "system_controller_unavailable",
            }
        try:
            return await _proxy_get(client, "/api/v1/network/wifi/state")
        except Exception:
            return {
                "timestamp_ms": now_ms,
                "enabled": None,
                "connected": False,
                "ssid": None,
                "bssid": None,
                "ip": None,
                "rssi_dbm": None,
                "link_quality": None,
                "last_update_ms": now_ms,
                "last_error": "system_controller_unavailable",
            }

    @app.get("/api/v1/network/wifi/scan")
    async def wifi_scan(request: Request) -> dict[str, Any]:
        client = _get_client(request, "system")
        now_ms = int(time.time() * 1000)
        if not client:
            return {"timestamp_ms": now_ms, "networks": []}
        try:
            return await _proxy_get(client, "/api/v1/network/wifi/scan")
        except Exception:
            return {"timestamp_ms": now_ms, "networks": [], "last_error": "system_controller_unavailable"}

    @app.get("/api/v1/network/bluetooth/state")
    async def bluetooth_state(request: Request) -> dict[str, Any]:
        client = _get_client(request, "system")
        now_ms = int(time.time() * 1000)
        if not client:
            return {
                "timestamp_ms": now_ms,
                "enabled": None,
                "scanning": None,
                "paired_count": 0,
                "connected_devices": [],
                "last_update_ms": now_ms,
                "last_error": "system_controller_unavailable",
            }
        try:
            return await _proxy_get(client, "/api/v1/network/bluetooth/state")
        except Exception:
            return {
                "timestamp_ms": now_ms,
                "enabled": None,
                "scanning": None,
                "paired_count": 0,
                "connected_devices": [],
                "last_update_ms": now_ms,
                "last_error": "system_controller_unavailable",
            }

    @app.get("/api/v1/network/bluetooth/devices")
    async def bluetooth_devices(request: Request) -> dict[str, Any]:
        client = _get_client(request, "system")
        now_ms = int(time.time() * 1000)
        if not client:
            return {"timestamp_ms": now_ms, "devices": []}
        try:
            return await _proxy_get(client, "/api/v1/network/bluetooth/devices")
        except Exception:
            return {"timestamp_ms": now_ms, "devices": [], "last_error": "system_controller_unavailable"}

    @app.post("/api/v1/network/wifi/enable", dependencies=[Depends(command_rate_limit)])
    async def wifi_enable(request: Request, body: CommandBody = COMMAND_BODY) -> dict[str, Any]:
        client = _get_client(request, "system")
        if not client:
            raise HTTPException(status_code=500, detail="system_controller_unavailable")
        return await _proxy_post(client, "/api/v1/network/wifi/enable", body.model_dump())

    @app.post("/api/v1/network/wifi/disable", dependencies=[Depends(command_rate_limit)])
    async def wifi_disable(request: Request, body: CommandBody = COMMAND_BODY) -> dict[str, Any]:
        client = _get_client(request, "system")
        if not client:
            raise HTTPException(status_code=500, detail="system_controller_unavailable")
        return await _proxy_post(client, "/api/v1/network/wifi/disable", body.model_dump())

    @app.post("/api/v1/network/wifi/connect", dependencies=[Depends(command_rate_limit)])
    async def wifi_connect(request: Request, body: CommandBody = COMMAND_BODY) -> dict[str, Any]:
        client = _get_client(request, "system")
        if not client:
            raise HTTPException(status_code=500, detail="system_controller_unavailable")
        return await _proxy_post(client, "/api/v1/network/wifi/connect", body.model_dump())

    @app.post("/api/v1/network/wifi/disconnect", dependencies=[Depends(command_rate_limit)])
    async def wifi_disconnect(request: Request, body: CommandBody = COMMAND_BODY) -> dict[str, Any]:
        client = _get_client(request, "system")
        if not client:
            raise HTTPException(status_code=500, detail="system_controller_unavailable")
        return await _proxy_post(client, "/api/v1/network/wifi/disconnect", body.model_dump())

    @app.post("/api/v1/network/bluetooth/enable", dependencies=[Depends(command_rate_limit)])
    async def bluetooth_enable(request: Request, body: CommandBody = COMMAND_BODY) -> dict[str, Any]:
        client = _get_client(request, "system")
        if not client:
            raise HTTPException(status_code=500, detail="system_controller_unavailable")
        return await _proxy_post(client, "/api/v1/network/bluetooth/enable", body.model_dump())

    @app.post("/api/v1/network/bluetooth/disable", dependencies=[Depends(command_rate_limit)])
    async def bluetooth_disable(request: Request, body: CommandBody = COMMAND_BODY) -> dict[str, Any]:
        client = _get_client(request, "system")
        if not client:
            raise HTTPException(status_code=500, detail="system_controller_unavailable")
        return await _proxy_post(client, "/api/v1/network/bluetooth/disable", body.model_dump())

    @app.post("/api/v1/network/bluetooth/scan/start", dependencies=[Depends(command_rate_limit)])
    async def bluetooth_scan_start(request: Request, body: CommandBody = COMMAND_BODY) -> dict[str, Any]:
        client = _get_client(request, "system")
        if not client:
            raise HTTPException(status_code=500, detail="system_controller_unavailable")
        return await _proxy_post(client, "/api/v1/network/bluetooth/scan/start", body.model_dump())

    @app.post("/api/v1/network/bluetooth/scan/stop", dependencies=[Depends(command_rate_limit)])
    async def bluetooth_scan_stop(request: Request, body: CommandBody = COMMAND_BODY) -> dict[str, Any]:
        client = _get_client(request, "system")
        if not client:
            raise HTTPException(status_code=500, detail="system_controller_unavailable")
        return await _proxy_post(client, "/api/v1/network/bluetooth/scan/stop", body.model_dump())

    @app.post("/api/v1/network/bluetooth/pair", dependencies=[Depends(command_rate_limit)])
    async def bluetooth_pair(request: Request, body: CommandBody = COMMAND_BODY) -> dict[str, Any]:
        client = _get_client(request, "system")
        if not client:
            raise HTTPException(status_code=500, detail="system_controller_unavailable")
        return await _proxy_post(client, "/api/v1/network/bluetooth/pair", body.model_dump())

    @app.post("/api/v1/network/bluetooth/unpair", dependencies=[Depends(command_rate_limit)])
    async def bluetooth_unpair(request: Request, body: CommandBody = COMMAND_BODY) -> dict[str, Any]:
        client = _get_client(request, "system")
        if not client:
            raise HTTPException(status_code=500, detail="system_controller_unavailable")
        return await _proxy_post(client, "/api/v1/network/bluetooth/unpair", body.model_dump())

    @app.post("/api/v1/services/{name}/restart")
    async def services_restart(name: str, request: Request, body: CommandBody = COMMAND_BODY) -> dict[str, Any]:
        require_confirm(body)
        await command_rate_limit(request)
        client = _get_client(request, "system")
        if not client:
            raise HTTPException(status_code=500, detail="system_controller_unavailable")
        return await _proxy_post(client, f"/api/v1/services/{name}/restart", body.model_dump())

    @app.post("/api/v1/gps/restart")
    async def gps_restart(request: Request, body: CommandBody = COMMAND_BODY) -> dict[str, Any]:
        require_confirm(body)
        await command_rate_limit(request)
        await dangerous_rate_limit(request)
        client = _get_client(request, "system")
        if not client:
            raise HTTPException(status_code=500, detail="system_controller_unavailable")
        return await _proxy_post(client, "/api/v1/gps/restart", body.model_dump())

    @app.post("/api/v1/audio/mute", dependencies=[Depends(command_rate_limit)])
    async def audio_mute(request: Request, body: CommandBody = COMMAND_BODY) -> dict[str, Any]:
        client = _get_client(request, "system")
        if not client:
            raise HTTPException(status_code=500, detail="system_controller_unavailable")
        return await _proxy_post(client, "/api/v1/audio/mute", body.model_dump())

    @app.post("/api/v1/audio/volume", dependencies=[Depends(command_rate_limit)])
    async def audio_volume(request: Request, body: CommandBody = COMMAND_BODY) -> dict[str, Any]:
        client = _get_client(request, "system")
        if not client:
            raise HTTPException(status_code=500, detail="system_controller_unavailable")
        return await _proxy_post(client, "/api/v1/audio/volume", body.model_dump())

    @app.get("/api/v1/antsdr/device")
    async def antsdr_device(request: Request) -> dict[str, Any]:
        client = _get_client(request, "antsdr")
        now_ms = int(time.time() * 1000)
        if not client:
            return {
                "timestamp_ms": now_ms,
                "connected": False,
                "uri": None,
                "temperature_c": None,
                "last_error": "antsdr_unavailable",
            }
        try:
            return await _proxy_get(client, "/api/v1/device")
        except Exception:
            return {
                "timestamp_ms": now_ms,
                "connected": False,
                "uri": None,
                "temperature_c": None,
                "last_error": "antsdr_unavailable",
            }

    @app.get("/api/v1/antsdr/sweep/state")
    async def antsdr_sweep_state(request: Request) -> dict[str, Any]:
        client = _get_client(request, "antsdr")
        now_ms = int(time.time() * 1000)
        if not client:
            return {"timestamp_ms": now_ms, "running": False, "plans": [], "last_update_ms": now_ms, "last_error": "antsdr_unavailable"}
        try:
            return await _proxy_get(client, "/api/v1/sweep/state")
        except Exception:
            return {
                "timestamp_ms": now_ms,
                "running": False,
                "plans": [],
                "last_update_ms": now_ms,
                "last_error": "antsdr_unavailable",
            }

    @app.get("/api/v1/antsdr/gain")
    async def antsdr_gain(request: Request) -> dict[str, Any]:
        client = _get_client(request, "antsdr")
        now_ms = int(time.time() * 1000)
        if not client:
            return {"timestamp_ms": now_ms, "mode": "auto", "gain_db": None}
        try:
            return await _proxy_get(client, "/api/v1/gain")
        except Exception:
            return {"timestamp_ms": now_ms, "mode": "auto", "gain_db": None}

    @app.get("/api/v1/antsdr/stats")
    async def antsdr_stats(request: Request) -> dict[str, Any]:
        client = _get_client(request, "antsdr")
        now_ms = int(time.time() * 1000)
        if not client:
            return {"timestamp_ms": now_ms, "frames_processed": 0, "events_emitted": 0}
        try:
            return await _proxy_get(client, "/api/v1/stats")
        except Exception:
            return {"timestamp_ms": now_ms, "frames_processed": 0, "events_emitted": 0}

    @app.post("/api/v1/antsdr/sweep/start", dependencies=[Depends(command_rate_limit)])
    async def antsdr_sweep_start(request: Request, body: CommandBody = COMMAND_BODY) -> dict[str, Any]:
        client = _get_client(request, "antsdr")
        if not client:
            raise HTTPException(status_code=500, detail="antsdr_unavailable")
        return await _proxy_post(client, "/api/v1/sweep/start", body.model_dump())

    @app.post("/api/v1/antsdr/sweep/stop", dependencies=[Depends(command_rate_limit)])
    async def antsdr_sweep_stop(request: Request, body: CommandBody = COMMAND_BODY) -> dict[str, Any]:
        client = _get_client(request, "antsdr")
        if not client:
            raise HTTPException(status_code=500, detail="antsdr_unavailable")
        return await _proxy_post(client, "/api/v1/sweep/stop", body.model_dump())

    @app.post("/api/v1/antsdr/gain/set", dependencies=[Depends(command_rate_limit)])
    async def antsdr_gain_set(request: Request, body: CommandBody = COMMAND_BODY) -> dict[str, Any]:
        client = _get_client(request, "antsdr")
        if not client:
            raise HTTPException(status_code=500, detail="antsdr_unavailable")
        return await _proxy_post(client, "/api/v1/gain/set", body.model_dump())

    @app.post("/api/v1/antsdr/device/reset")
    async def antsdr_device_reset(request: Request, body: CommandBody = COMMAND_BODY) -> dict[str, Any]:
        require_confirm(body)
        await command_rate_limit(request)
        await dangerous_rate_limit(request)
        client = _get_client(request, "antsdr")
        if not client:
            raise HTTPException(status_code=500, detail="antsdr_unavailable")
        return await _proxy_post(client, "/api/v1/device/reset", body.model_dump())

    @app.post("/api/v1/antsdr/device/calibrate")
    async def antsdr_device_calibrate(request: Request, body: CommandBody = COMMAND_BODY) -> dict[str, Any]:
        require_confirm(body)
        await command_rate_limit(request)
        await dangerous_rate_limit(request)
        client = _get_client(request, "antsdr")
        if not client:
            raise HTTPException(status_code=500, detail="antsdr_unavailable")
        return await _proxy_post(client, "/api/v1/device/calibrate", body.model_dump())

    @app.get("/api/v1/remote_id/status")
    async def remoteid_status(request: Request) -> dict[str, Any]:
        client = _get_client(request, "remoteid")
        if not client:
            snapshot = await state_store.snapshot()
            return snapshot.remote_id
        try:
            return await _proxy_get(client, "/api/v1/status")
        except Exception:
            snapshot = await state_store.snapshot()
            if "timestamp_ms" not in snapshot.remote_id:
                snapshot.remote_id["timestamp_ms"] = int(time.time() * 1000)
            return snapshot.remote_id

    @app.get("/api/v1/remote_id")
    async def remoteid_status_alias(request: Request) -> dict[str, Any]:
        return await remoteid_status(request)

    @app.get("/api/v1/remote_id/contacts")
    async def remoteid_contacts(request: Request) -> dict[str, Any]:
        client = _get_client(request, "remoteid")
        now_ms = int(time.time() * 1000)
        if not client:
            snapshot = await state_store.snapshot()
            return {"timestamp_ms": now_ms, "contacts": snapshot.contacts}
        try:
            return await _proxy_get(client, "/api/v1/contacts")
        except Exception:
            snapshot = await state_store.snapshot()
            return {"timestamp_ms": now_ms, "contacts": snapshot.contacts}

    @app.get("/api/v1/remote_id/stats")
    async def remoteid_stats(request: Request) -> dict[str, Any]:
        client = _get_client(request, "remoteid")
        now_ms = int(time.time() * 1000)
        if not client:
            return {"timestamp_ms": now_ms, "frames": 0, "decoded": 0}
        try:
            return await _proxy_get(client, "/api/v1/stats")
        except Exception:
            return {"timestamp_ms": now_ms, "frames": 0, "decoded": 0}

    @app.post("/api/v1/remote_id/monitor/start", dependencies=[Depends(command_rate_limit)])
    async def remoteid_monitor_start(request: Request, body: CommandBody = COMMAND_BODY) -> dict[str, Any]:
        client = _get_client(request, "remoteid")
        if not client:
            raise HTTPException(status_code=500, detail="remoteid_unavailable")
        return await _proxy_post(client, "/api/v1/monitor/start", body.model_dump())

    @app.post("/api/v1/remote_id/monitor/stop", dependencies=[Depends(command_rate_limit)])
    async def remoteid_monitor_stop(request: Request, body: CommandBody = COMMAND_BODY) -> dict[str, Any]:
        client = _get_client(request, "remoteid")
        if not client:
            raise HTTPException(status_code=500, detail="remoteid_unavailable")
        return await _proxy_post(client, "/api/v1/monitor/stop", body.model_dump())

    @app.get("/api/v1/remote_id/replay/state")
    async def remoteid_replay_state(request: Request) -> dict[str, Any]:
        client = _get_client(request, "remoteid")
        now_ms = int(time.time() * 1000)
        if not client:
            return {"timestamp_ms": now_ms, "active": False, "source": "none"}
        try:
            return await _proxy_get(client, "/api/v1/replay/state")
        except Exception:
            return {"timestamp_ms": now_ms, "active": False, "source": "none"}

    @app.post("/api/v1/remote_id/replay/start", dependencies=[Depends(command_rate_limit)])
    async def remoteid_replay_start(request: Request, body: CommandBody = COMMAND_BODY) -> dict[str, Any]:
        client = _get_client(request, "remoteid")
        if not client:
            raise HTTPException(status_code=500, detail="remoteid_unavailable")
        return await _proxy_post(client, "/api/v1/replay/start", body.model_dump())

    @app.post("/api/v1/remote_id/replay/stop", dependencies=[Depends(command_rate_limit)])
    async def remoteid_replay_stop(request: Request, body: CommandBody = COMMAND_BODY) -> dict[str, Any]:
        client = _get_client(request, "remoteid")
        if not client:
            raise HTTPException(status_code=500, detail="remoteid_unavailable")
        return await _proxy_post(client, "/api/v1/replay/stop", body.model_dump())

    @app.get("/api/v1/esp32/config")
    async def esp32_config() -> dict[str, Any]:
        now_ms = int(time.time() * 1000)
        return {"timestamp_ms": now_ms, "schema_version": None, "config": {}}

    @app.post("/api/v1/esp32/config", dependencies=[Depends(command_rate_limit)])
    async def esp32_config_set(request: Request, body: CommandBody = COMMAND_BODY) -> dict[str, Any]:
        return await _dispatch_local_command(request, "esp32/config", body)

    @app.post("/api/v1/esp32/buzzer", dependencies=[Depends(command_rate_limit)])
    async def esp32_buzzer(request: Request, body: CommandBody = COMMAND_BODY) -> dict[str, Any]:
        return await _dispatch_local_command(request, "esp32/buzzer", body)

    @app.post("/api/v1/esp32/leds", dependencies=[Depends(command_rate_limit)])
    async def esp32_leds(request: Request, body: CommandBody = COMMAND_BODY) -> dict[str, Any]:
        return await _dispatch_local_command(request, "esp32/leds", body)

    @app.post("/api/v1/esp32/buttons/simulate", dependencies=[Depends(command_rate_limit)])
    async def esp32_buttons(request: Request, body: CommandBody = COMMAND_BODY) -> dict[str, Any]:
        require_local(request)
        return await _dispatch_local_command(request, "esp32/buttons/simulate", body)

    @app.post("/api/v1/esp32/vrx/tune", dependencies=[Depends(command_rate_limit)])
    async def esp32_vrx_tune(request: Request, body: CommandBody = COMMAND_BODY) -> dict[str, Any]:
        return await _dispatch_local_command(request, "vrx/tune", body)

    @app.post("/api/v1/esp32/video/select", dependencies=[Depends(command_rate_limit)])
    async def esp32_video_select(request: Request, body: CommandBody = COMMAND_BODY) -> dict[str, Any]:
        return await _dispatch_local_command(request, "video/select", body)


async def _dispatch_local_command(request: Request, command: str, body: CommandBody) -> dict[str, Any]:
    cmd_request = CommandRequest(
        command=command,
        payload=body.payload,
        confirm=body.confirm,
        issued_by=request.client.host if request.client else None,
    )
    command_router: CommandRouter = request.app.state.command_router
    result = await command_router.dispatch(cmd_request)
    if not result.accepted:
        raise HTTPException(status_code=409, detail=result.detail or "invalid_state")
    return result.model_dump()


def _register_ws_routes(app: FastAPI, ws_manager: WebSocketManager) -> None:
    config = get_config()
    allowed_origins = set(config.cors.allow_origins)
    origin_pattern = (
        re.compile(config.cors.allow_origin_regex)
        if config.cors.allow_origin_regex
        else None
    )
    allow_all = "*" in allowed_origins

    def origin_allowed(origin: str | None) -> bool:
        if allow_all:
            return True
        if not origin:
            return False
        if origin in allowed_origins:
            return True
        return bool(origin_pattern and origin_pattern.match(origin))

    @app.options("/api/v1/ws")
    async def ws_preflight() -> Response:
        return Response(status_code=200)

    @app.websocket("/api/v1/ws")
    async def ws_endpoint(websocket: WebSocket) -> None:
        if not origin_allowed(websocket.headers.get("origin")):
            await websocket.close(code=1008)
            return
        await ws_manager.connect(websocket)
        heartbeat_task: asyncio.Task[None] | None = None
        try:
            now_ms = int(time.time() * 1000)
            hello = EventEnvelope(
                type="HELLO",
                timestamp_ms=now_ms,
                source="aggregator",
                data={"timestamp_ms": now_ms},
            )
            await websocket.send_json(hello.model_dump())
            await ws_manager.send_system_update(websocket)

            async def heartbeat_loop() -> None:
                while True:
                    ts = int(time.time() * 1000)
                    envelope = EventEnvelope(
                        type="HEARTBEAT",
                        timestamp_ms=ts,
                        source="aggregator",
                        data={"timestamp_ms": ts},
                    )
                    await websocket.send_json(envelope.model_dump())
                    await asyncio.sleep(2)

            heartbeat_task = asyncio.create_task(heartbeat_loop())
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            pass
        finally:
            if heartbeat_task:
                heartbeat_task.cancel()
                with suppress(asyncio.CancelledError):
                    await heartbeat_task
            await ws_manager.disconnect(websocket)


async def _forward_events(event_bus: EventBus, ws_manager: WebSocketManager) -> None:
    queue = await event_bus.subscribe()
    try:
        while True:
            event = await queue.get()
            await ws_manager.broadcast(event.model_dump())
    finally:
        await event_bus.unsubscribe(queue)


def _register_routes(
    app: FastAPI,
    state_store: StateStore,
    ws_manager: WebSocketManager,
    config,
    command_router: CommandRouter,
) -> None:
    _register_read_routes(app, state_store)
    _register_command_routes(app, config, command_router)
    _register_proxy_routes(app, state_store)
    _register_ws_routes(app, ws_manager)


def create_app() -> FastAPI:
    config = get_config()
    configure_logging(config.logging.level)

    state_store = StateStore()
    event_bus = EventBus()
    ws_manager = WebSocketManager(state_store)
    contact_store = ContactStore(state_store)
    orchestrator = build_default_orchestrator(config, state_store, event_bus, contact_store)
    command_router = CommandRouter()
    esp32_ingestor = next(
        (ingestor for ingestor in orchestrator.ingestors if isinstance(ingestor, Esp32Ingestor)),
        None,
    )
    if esp32_ingestor:
        command_router.register(Esp32CommandHandler(esp32_ingestor))
    command_router.register(SystemCommandHandler(config))

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await orchestrator.start()
        forward_task = asyncio.create_task(_forward_events(event_bus, ws_manager))
        yield
        forward_task.cancel()
        with suppress(asyncio.CancelledError):
            await forward_task
        await orchestrator.stop()
        clients = list(app.state.http_clients.values())
        for client in clients:
            await client.aclose()

    app = FastAPI(
        title="N-Defender Backend Aggregator",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=config.cors.max_age,
    )

    app.state.state_store = state_store
    app.state.event_bus = event_bus
    app.state.ws_manager = ws_manager
    app.state.runtime = orchestrator
    app.state.contact_store = contact_store
    app.state.command_router = command_router
    app.state.http_clients = {
        "system": httpx.AsyncClient(
            base_url=config.system_controller.base_url,
            timeout=config.system_controller.timeout_seconds,
        ),
        "antsdr": httpx.AsyncClient(
            base_url=config.antsdr.base_url,
            timeout=config.antsdr.timeout_seconds,
        ),
        "remoteid": httpx.AsyncClient(
            base_url=config.remoteid.base_url,
            timeout=config.remoteid.timeout_seconds,
        ),
    }

    _register_routes(app, state_store, ws_manager, config, command_router)
    return app


app = create_app()
