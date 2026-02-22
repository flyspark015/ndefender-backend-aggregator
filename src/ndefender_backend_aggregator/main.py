"""FastAPI entrypoint."""

from __future__ import annotations

import time
import uuid
from contextlib import asynccontextmanager
from typing import Any

import re

from fastapi import Body, Depends, FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .auth import api_key_auth
from .bus import EventBus
from .commands import CommandRequest, CommandRouter, Esp32CommandHandler, SystemCommandHandler
from .config import get_config
from .contacts import ContactStore
from .integrations.esp32_serial import Esp32Ingestor
from .logging import configure_logging
from .models import StatusSnapshot
from .rate_limit import command_rate_limit, dangerous_rate_limit
from .rbac import require_permission
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
        raise HTTPException(status_code=400, detail="confirm=true required")


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
        snapshot = await state_store.snapshot()
        return {"contacts": snapshot.contacts}

    @app.get("/api/v1/system", dependencies=[Depends(api_key_auth), read_guard])
    async def system() -> dict[str, Any]:
        snapshot = await state_store.snapshot()
        return snapshot.system

    @app.get("/api/v1/power", dependencies=[Depends(api_key_auth), read_guard])
    async def power() -> dict[str, Any]:
        snapshot = await state_store.snapshot()
        return snapshot.power

    @app.get("/api/v1/rf", dependencies=[Depends(api_key_auth), read_guard])
    async def rf() -> dict[str, Any]:
        snapshot = await state_store.snapshot()
        return snapshot.rf

    @app.get("/api/v1/video", dependencies=[Depends(api_key_auth), read_guard])
    async def video() -> dict[str, Any]:
        snapshot = await state_store.snapshot()
        return snapshot.video

    @app.get("/api/v1/services", dependencies=[Depends(api_key_auth), read_guard])
    async def services() -> list[dict[str, Any]]:
        snapshot = await state_store.snapshot()
        return snapshot.services

    @app.get("/api/v1/network", dependencies=[Depends(api_key_auth), read_guard])
    async def network() -> dict[str, Any]:
        snapshot = await state_store.snapshot()
        return snapshot.network

    @app.get("/api/v1/audio", dependencies=[Depends(api_key_auth), read_guard])
    async def audio() -> dict[str, Any]:
        snapshot = await state_store.snapshot()
        return snapshot.audio


def _register_command_routes(app: FastAPI, config, command_router: CommandRouter) -> None:
    device_guard = Depends(require_permission("device_control"))
    system_guard = Depends(require_permission("system_control"))

    async def dispatch_command(
        command: str,
        body: CommandBody,
        request: Request,
    ) -> dict[str, Any]:
        cmd_request = CommandRequest(
            command=command,
            payload=body.payload,
            confirm=body.confirm,
            issued_by=request.headers.get("X-Role"),
        )
        result = await command_router.dispatch(cmd_request)
        return result.model_dump()

    @app.post(
        "/api/v1/vrx/tune",
        dependencies=[Depends(api_key_auth), device_guard, Depends(command_rate_limit)],
    )
    async def vrx_tune(
        request: Request,
        body: CommandBody = COMMAND_BODY,
    ) -> dict[str, Any]:
        return await dispatch_command("vrx/tune", body, request)

    @app.post(
        "/api/v1/scan/start",
        dependencies=[Depends(api_key_auth), device_guard, Depends(command_rate_limit)],
    )
    async def scan_start(
        request: Request,
        body: CommandBody = COMMAND_BODY,
    ) -> dict[str, Any]:
        return await dispatch_command("scan/start", body, request)

    @app.post(
        "/api/v1/scan/stop",
        dependencies=[Depends(api_key_auth), device_guard, Depends(command_rate_limit)],
    )
    async def scan_stop(
        request: Request,
        body: CommandBody = COMMAND_BODY,
    ) -> dict[str, Any]:
        return await dispatch_command("scan/stop", body, request)

    @app.post(
        "/api/v1/video/select",
        dependencies=[Depends(api_key_auth), device_guard, Depends(command_rate_limit)],
    )
    async def video_select(
        request: Request,
        body: CommandBody = COMMAND_BODY,
    ) -> dict[str, Any]:
        return await dispatch_command("video/select", body, request)

    @app.post(
        "/api/v1/system/reboot",
        dependencies=[
            Depends(api_key_auth),
            system_guard,
            Depends(command_rate_limit),
            Depends(dangerous_rate_limit),
        ],
    )
    async def system_reboot(
        request: Request,
        body: CommandBody = COMMAND_BODY,
    ) -> dict[str, Any]:
        require_confirm(body)
        if not config.safety.allow_unsafe_operations:
            raise HTTPException(status_code=403, detail="Unsafe operations disabled")
        return await dispatch_command("system/reboot", body, request)

    @app.post(
        "/api/v1/system/shutdown",
        dependencies=[
            Depends(api_key_auth),
            system_guard,
            Depends(command_rate_limit),
            Depends(dangerous_rate_limit),
        ],
    )
    async def system_shutdown(
        request: Request,
        body: CommandBody = COMMAND_BODY,
    ) -> dict[str, Any]:
        require_confirm(body)
        if not config.safety.allow_unsafe_operations:
            raise HTTPException(status_code=403, detail="Unsafe operations disabled")
        return await dispatch_command("system/shutdown", body, request)


def _register_ws_routes(app: FastAPI, ws_manager: WebSocketManager) -> None:
    config = get_config()
    allowed_origins = set(config.cors.allow_origins)
    origin_pattern = (
        re.compile(config.cors.allow_origin_regex)
        if config.cors.allow_origin_regex
        else None
    )

    def origin_allowed(origin: str | None) -> bool:
        if not origin:
            return False
        if origin in allowed_origins:
            return True
        if origin_pattern and origin_pattern.match(origin):
            return True
        return False

    @app.websocket("/api/v1/ws")
    async def ws_endpoint(websocket: WebSocket) -> None:
        if not origin_allowed(websocket.headers.get("origin")):
            await websocket.close(code=1008)
            return
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
    command_router: CommandRouter,
) -> None:
    _register_read_routes(app, state_store)
    _register_command_routes(app, config, command_router)
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
        yield
        await orchestrator.stop()

    app = FastAPI(
        title="N-Defender Backend Aggregator",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors.allow_origins,
        allow_origin_regex=config.cors.allow_origin_regex,
        allow_credentials=config.cors.allow_credentials,
        allow_methods=config.cors.allow_methods,
        allow_headers=config.cors.allow_headers,
        max_age=config.cors.max_age,
    )

    app.state.state_store = state_store
    app.state.event_bus = event_bus
    app.state.ws_manager = ws_manager
    app.state.runtime = orchestrator
    app.state.contact_store = contact_store
    app.state.command_router = command_router

    _register_routes(app, state_store, ws_manager, config, command_router)
    return app


app = create_app()
