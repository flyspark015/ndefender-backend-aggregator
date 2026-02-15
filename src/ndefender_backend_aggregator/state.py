"""Central async state store."""

from __future__ import annotations

import asyncio
import copy
import time
from typing import Any

from .models import StatusSnapshot


class StateStore:
    """Thread-safe state container for subsystem snapshots."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._state: dict[str, Any] = {
            "system": {},
            "power": {},
            "rf": {},
            "remote_id": {},
            "vrx": {},
            "video": {},
            "services": [],
            "network": {},
            "audio": {},
            "contacts": [],
            "replay": {"active": False, "source": "none"},
        }

    async def update_section(self, name: str, data: dict[str, Any]) -> None:
        async with self._lock:
            if name not in self._state:
                raise KeyError(f"Unknown state section: {name}")
            self._state[name] = data

    async def snapshot(self) -> StatusSnapshot:
        async with self._lock:
            snapshot = copy.deepcopy(self._state)
        snapshot["timestamp_ms"] = int(time.time() * 1000)
        return StatusSnapshot.model_validate(snapshot)
