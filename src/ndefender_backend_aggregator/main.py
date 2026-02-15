"""FastAPI entrypoint."""

from __future__ import annotations

import time
import uuid
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect

from .auth import api_key_auth
from .bus import EventBus
from .config import get_config
from .logging import configure_logging
from .models import StatusSnapshot
from .rate_limit import command_rate_limit, dangerous_rate_limit
from .rbac import require_permission
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


def _register_read_routes(app: FastAPI, state_store: StateStore) -> None:
    read_guard = Depends(require_permission("read"))

    @app.get("/api/v1/health", dependencies=[Depends(api_key_auth), read_guard])
    async def health() -> dict[str, Any]:
        return {"status": "ok", "timestamp_ms": int(time.time() * 1000)}

    @app.get("/api/v1/status", dependencies=[Depends(api_key_auth), read_guard])
    async def status() -> StatusSnapshot:
        return await state_store.snapshot()

    @app.get("/api/v1/contacts", dependencies=[Depends(api_key_auth), read_guard])
    async def contacts() -> dict[str, Any]:
        return {"contacts": []}

    @app.get("/api/v1/system", dependencies=[Depends(api_key_auth), read_guard])
    async def system() -> dict[str, Any]:
        snapshot = await state_store.snapshot()
        return snapshot.get("system", {})

    @app.get("/api/v1/power", dependencies=[Depends(api_key_auth), read_guard])
    async def power() -> dict[str, Any]:
        snapshot = await state_store.snapshot()
        return snapshot.get("power", {})

    @app.get("/api/v1/rf", dependencies=[Depends(api_key_auth), read_guard])
    async def rf() -> dict[str, Any]:
        snapshot = await state_store.snapshot()
        return snapshot.get("rf", {})

    @app.get("/api/v1/video", dependencies=[Depends(api_key_auth), read_guard])
    async def video() -> dict[str, Any]:
        snapshot = await state_store.snapshot()
        return snapshot.get("video", {})

    @app.get("/api/v1/services", dependencies=[Depends(api_key_auth), read_guard])
    async def services() -> dict[str, Any]:
        snapshot = await state_store.snapshot()
        return snapshot.get("services", {})


def _register_command_routes(app: FastAPI, config) -> None:
    device_guard = Depends(require_permission("device_control"))
    system_guard = Depends(require_permission("system_control"))

    @app.post(
        "/api/v1/vrx/tune",
        dependencies=[Depends(api_key_auth), device_guard, Depends(command_rate_limit)],
    )
    async def vrx_tune() -> dict[str, Any]:
        ack = CommandAck("vrx/tune", accepted=False, detail="Not implemented")
        raise HTTPException(status_code=501, detail=ack.model_dump())

    @app.post(
        "/api/v1/scan/start",
        dependencies=[Depends(api_key_auth), device_guard, Depends(command_rate_limit)],
    )
    async def scan_start() -> dict[str, Any]:
        ack = CommandAck("scan/start", accepted=False, detail="Not implemented")
        raise HTTPException(status_code=501, detail=ack.model_dump())

    @app.post(
        "/api/v1/scan/stop",
        dependencies=[Depends(api_key_auth), device_guard, Depends(command_rate_limit)],
    )
    async def scan_stop() -> dict[str, Any]:
        ack = CommandAck("scan/stop", accepted=False, detail="Not implemented")
        raise HTTPException(status_code=501, detail=ack.model_dump())

    @app.post(
        "/api/v1/video/select",
        dependencies=[Depends(api_key_auth), device_guard, Depends(command_rate_limit)],
    )
    async def video_select() -> dict[str, Any]:
        ack = CommandAck("video/select", accepted=False, detail="Not implemented")
        raise HTTPException(status_code=501, detail=ack.model_dump())

    @app.post(
        "/api/v1/system/reboot",
        dependencies=[
            Depends(api_key_auth),
            system_guard,
            Depends(command_rate_limit),
            Depends(dangerous_rate_limit),
        ],
    )
    async def system_reboot(confirm: bool = False) -> dict[str, Any]:
        if not confirm:
            raise HTTPException(status_code=400, detail="confirm=true required")
        if not config.safety.allow_unsafe_operations:
            raise HTTPException(status_code=403, detail="Unsafe operations disabled")
        ack = CommandAck("system/reboot", accepted=False, detail="Not implemented")
        raise HTTPException(status_code=501, detail=ack.model_dump())

    @app.post(
        "/api/v1/system/shutdown",
        dependencies=[
            Depends(api_key_auth),
            system_guard,
            Depends(command_rate_limit),
            Depends(dangerous_rate_limit),
        ],
    )
    async def system_shutdown(confirm: bool = False) -> dict[str, Any]:
        if not confirm:
            raise HTTPException(status_code=400, detail="confirm=true required")
        if not config.safety.allow_unsafe_operations:
            raise HTTPException(status_code=403, detail="Unsafe operations disabled")
        ack = CommandAck("system/shutdown", accepted=False, detail="Not implemented")
        raise HTTPException(status_code=501, detail=ack.model_dump())


def _register_ws_routes(app: FastAPI, ws_manager: WebSocketManager) -> None:
    @app.websocket("/api/v1/ws")
    async def ws_endpoint(websocket: WebSocket) -> None:
        await ws_manager.connect(websocket)
        try:
            await ws_manager.send_system_update(websocket)
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            await ws_manager.disconnect(websocket)


def _register_routes(
    app: FastAPI,
    state_store: StateStore,
    ws_manager: WebSocketManager,
    config,
) -> None:
    _register_read_routes(app, state_store)
    _register_command_routes(app, config)
    _register_ws_routes(app, ws_manager)


def create_app() -> FastAPI:
    config = get_config()
    configure_logging(config.logging.level)

    app = FastAPI(title="N-Defender Backend Aggregator", version="0.1.0")
    state_store = StateStore()
    event_bus = EventBus()
    ws_manager = WebSocketManager(state_store)

    app.state.state_store = state_store
    app.state.event_bus = event_bus
    app.state.ws_manager = ws_manager

    _register_routes(app, state_store, ws_manager, config)
    return app


app = create_app()
