"""System Controller command handler."""

from __future__ import annotations

import time
import uuid

import httpx

from ..config import AppConfig
from .contracts import CommandHandler, CommandRequest, CommandResult


class SystemCommandHandler(CommandHandler):
    def __init__(self, config: AppConfig, client: httpx.AsyncClient | None = None) -> None:
        self._config = config
        self._client = client

    def can_handle(self, command: str) -> bool:
        return command in {
            "system/reboot",
            "system/shutdown",
            "services/restart",
        }

    async def handle(self, request: CommandRequest) -> CommandResult:
        if request.command in {"system/reboot", "system/shutdown"}:
            return await self._handle_power(request)
        if request.command == "services/restart":
            return await self._handle_service_restart(request)
        return self._result(request.command, False, "unsupported")

    async def _handle_power(self, request: CommandRequest) -> CommandResult:
        if not request.confirm:
            return self._result(request.command, False, "confirm required")
        if not self._config.safety.allow_unsafe_operations:
            return self._result(request.command, False, "unsafe operations disabled")
        endpoint = (
            "/api/v1/system/reboot"
            if request.command.endswith("reboot")
            else "/api/v1/system/shutdown"
        )
        payload = {"confirm": True}
        return await self._post(endpoint, payload, request.command)

    async def _handle_service_restart(self, request: CommandRequest) -> CommandResult:
        service = request.payload.get("service")
        if not service:
            return self._result(request.command, False, "service required")
        endpoint = f"/api/v1/services/{service}/restart"
        return await self._post(endpoint, {}, request.command)

    async def _post(
        self,
        endpoint: str,
        payload: dict[str, object],
        command: str,
    ) -> CommandResult:
        client = self._client or httpx.AsyncClient(
            base_url=self._config.system_controller.base_url,
            timeout=self._config.system_controller.timeout_seconds,
        )
        headers = {}
        if self._config.system_controller.api_key:
            headers["X-API-Key"] = self._config.system_controller.api_key
        command_id = str(uuid.uuid4())
        try:
            response = await client.post(endpoint, json=payload, headers=headers)
            response.raise_for_status()
            return self._result(command, True, None, command_id)
        except Exception as exc:
            return self._result(command, False, str(exc), command_id)
        finally:
            if self._client is None:
                await client.aclose()

    @staticmethod
    def _result(
        command: str,
        accepted: bool,
        detail: str | None,
        command_id: str | None = None,
    ) -> CommandResult:
        return CommandResult(
            command=command,
            command_id=command_id or str(uuid.uuid4()),
            accepted=accepted,
            detail=detail,
            timestamp_ms=int(time.time() * 1000),
        )
