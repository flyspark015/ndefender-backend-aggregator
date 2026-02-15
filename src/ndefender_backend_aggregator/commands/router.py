"""Command router for dispatching requests to handlers."""

from __future__ import annotations

import time
import uuid
from collections.abc import Iterable

from .contracts import CommandHandler, CommandRequest, CommandResult


class CommandRouter:
    def __init__(self, handlers: Iterable[CommandHandler] | None = None) -> None:
        self._handlers: list[CommandHandler] = list(handlers or [])

    def register(self, handler: CommandHandler) -> None:
        self._handlers.append(handler)

    async def dispatch(self, request: CommandRequest) -> CommandResult:
        for handler in self._handlers:
            if handler.can_handle(request.command):
                return await handler.handle(request)
        return CommandResult(
            command=request.command,
            command_id=str(uuid.uuid4()),
            accepted=False,
            detail="No handler registered for command",
            timestamp_ms=int(time.time() * 1000),
        )
