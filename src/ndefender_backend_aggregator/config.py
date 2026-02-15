"""Configuration loading and validation."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field


class SystemControllerConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    base_url: str
    timeout_seconds: int = Field(ge=1)
    api_key: str | None = None


class Esp32Config(BaseModel):
    model_config = ConfigDict(extra="forbid")

    serial_port: str
    baud_rate: int = Field(ge=1)
    reconnect_delay_seconds: int = Field(ge=1)


class AntsdrConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    jsonl_path: str
    tail_poll_interval_ms: int = Field(ge=1)


class RemoteIdConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    jsonl_path: str
    tail_poll_interval_ms: int = Field(ge=1)


class AuthConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key_required: bool
    api_key: str
    rbac_enabled: bool


class RoleConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    permissions: list[str]


class RbacConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    roles: dict[str, RoleConfig]


class SafetyConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    allow_unsafe_operations: bool
    reboot_cooldown_seconds: int = Field(ge=1)
    shutdown_cooldown_seconds: int = Field(ge=1)


class PollingConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    system_controller_interval_ms: int = Field(ge=1)
    ups_interval_ms: int = Field(ge=1)
    network_interval_ms: int = Field(ge=1)
    audio_interval_ms: int = Field(ge=1)


class LoggingConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    level: str


class RateLimitConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dangerous_per_minute: int = Field(ge=1)
    command_per_minute: int = Field(ge=1)


class FeaturesConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enable_antsdr: bool
    enable_remoteid: bool
    enable_esp32: bool


class AppConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    system_controller: SystemControllerConfig
    esp32: Esp32Config
    antsdr: AntsdrConfig
    remoteid: RemoteIdConfig
    auth: AuthConfig
    rbac: RbacConfig
    safety: SafetyConfig
    polling: PollingConfig
    logging: LoggingConfig
    rate_limits: RateLimitConfig
    features: FeaturesConfig


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Config file must be a mapping: {path}")
    return data


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _load_config() -> AppConfig:
    default_path = _repo_root() / "config" / "default.yaml"
    data = _load_yaml(default_path)

    override_path = os.getenv("NDEFENDER_CONFIG")
    if override_path:
        override_data = _load_yaml(Path(override_path))
        data = _deep_merge(data, override_data)

    return AppConfig.model_validate(data)


@lru_cache(maxsize=1)
def get_config() -> AppConfig:
    return _load_config()
