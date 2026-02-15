"""ESP32 command handler."""

from __future__ import annotations

from typing import Any

from ..integrations.esp32_serial import Esp32Ingestor
from .contracts import CommandHandler, CommandRequest, CommandResult


class Esp32CommandHandler(CommandHandler):
    def __init__(self, ingestor: Esp32Ingestor) -> None:
        self._ingestor = ingestor

    def can_handle(self, command: str) -> bool:
        return command in {
            "vrx/tune",
            "scan/start",
            "scan/stop",
            "video/select",
        }

    async def handle(self, request: CommandRequest) -> CommandResult:
        mapping: dict[str, tuple[str, dict[str, Any]]] = {
            "vrx/tune": ("SET_VRX_FREQ", request.payload or {}),
            "scan/start": ("START_SCAN", request.payload or {}),
            "scan/stop": ("STOP_SCAN", request.payload or {}),
            "video/select": ("VIDEO_SELECT", request.payload or {}),
        }
        esp_cmd, args = mapping[request.command]
        return await self._ingestor.send_command(esp_cmd, args)
