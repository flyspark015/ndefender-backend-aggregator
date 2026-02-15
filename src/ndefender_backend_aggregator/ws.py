"""WebSocket management."""

from __future__ import annotations

import asyncio
from typing import Any

from fastapi import WebSocket

from .state import StateStore


class WebSocketManager:
    def __init__(self, state_store: StateStore) -> None:
        self._state_store = state_store
        self._connections: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections.add(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._connections.discard(websocket)

    async def broadcast(self, message: dict[str, Any]) -> None:
        async with self._lock:
            connections = list(self._connections)
        for websocket in connections:
            await websocket.send_json(message)

    async def send_system_update(self, websocket: WebSocket) -> None:
        snapshot = await self._state_store.snapshot()
        await websocket.send_json(
            {
                "type": "SYSTEM_UPDATE",
                "timestamp_ms": snapshot["timestamp_ms"],
                "source": "aggregator",
                "data": snapshot,
            }
        )
