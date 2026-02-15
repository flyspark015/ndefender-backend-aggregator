"""Contracts for command routing."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


@dataclass(frozen=True)
class CommandRequest:
    command: str
    payload: dict[str, Any] = field(default_factory=dict)
    confirm: bool = False
    issued_by: str | None = None


class CommandResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command: str
    command_id: str
    accepted: bool
    detail: str | None = None
    timestamp_ms: int = Field(ge=0)


class CommandHandler(ABC):
    @abstractmethod
    def can_handle(self, command: str) -> bool:
        """Return True if this handler supports the command."""

    @abstractmethod
    async def handle(self, request: CommandRequest) -> CommandResult:
        """Handle command request and return result."""
