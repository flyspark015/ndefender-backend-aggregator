"""Pydantic models for canonical state and events."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class StatusSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    timestamp_ms: int = Field(ge=0)
    system: dict[str, Any] = Field(default_factory=dict)
    power: dict[str, Any] = Field(default_factory=dict)
    rf: dict[str, Any] = Field(default_factory=dict)
    remote_id: dict[str, Any] = Field(default_factory=dict)
    vrx: dict[str, Any] = Field(default_factory=dict)
    video: dict[str, Any] = Field(default_factory=dict)
    services: list[dict[str, Any]] = Field(default_factory=list)
    network: dict[str, Any] = Field(default_factory=dict)
    audio: dict[str, Any] = Field(default_factory=dict)
    contacts: list[dict[str, Any]] = Field(default_factory=list)
    replay: dict[str, Any] = Field(default_factory=dict)


class EventEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    timestamp_ms: int = Field(ge=0)
    source: str
    data: dict[str, Any]
