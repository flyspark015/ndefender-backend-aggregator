"""Internal event bus for decoupled ingestion and broadcasting."""

from __future__ import annotations

import asyncio
from collections.abc import Iterable

from .models import EventEnvelope


class EventBus:
    def __init__(self, max_queue_size: int = 1000) -> None:
        if max_queue_size < 1:
            raise ValueError("max_queue_size must be >= 1")
        self._max_queue_size = max_queue_size
        self._subscribers: set[asyncio.Queue[EventEnvelope]] = set()
        self._lock = asyncio.Lock()

    async def subscribe(self) -> asyncio.Queue[EventEnvelope]:
        queue: asyncio.Queue[EventEnvelope] = asyncio.Queue(maxsize=self._max_queue_size)
        async with self._lock:
            self._subscribers.add(queue)
        return queue

    async def unsubscribe(self, queue: asyncio.Queue[EventEnvelope]) -> None:
        async with self._lock:
            self._subscribers.discard(queue)

    async def publish(self, event: EventEnvelope) -> None:
        subscribers = await self._snapshot_subscribers()
        for queue in subscribers:
            self._enqueue(queue, event)

    async def _snapshot_subscribers(self) -> Iterable[asyncio.Queue[EventEnvelope]]:
        async with self._lock:
            return list(self._subscribers)

    def _enqueue(self, queue: asyncio.Queue[EventEnvelope], event: EventEnvelope) -> None:
        try:
            queue.put_nowait(event)
        except asyncio.QueueFull:
            try:
                _ = queue.get_nowait()
            except asyncio.QueueEmpty:
                return
            queue.put_nowait(event)
