"""Runtime orchestration for lifecycle management."""

from __future__ import annotations

import asyncio
from collections.abc import Iterable

from .bus import EventBus
from .config import AppConfig
from .ingest import Ingestor
from .integrations import (
    AntsdrIngestor,
    Esp32Ingestor,
    RemoteIdIngestor,
    SystemControllerIngestor,
)
from .state import StateStore


class RuntimeOrchestrator:
    def __init__(self, ingestors: Iterable[Ingestor]) -> None:
        self._ingestors = list(ingestors)
        self._running = False

    @property
    def ingestors(self) -> list[Ingestor]:
        return list(self._ingestors)

    async def start(self) -> None:
        if self._running:
            return
        await asyncio.gather(*(ingestor.start() for ingestor in self._ingestors))
        self._running = True

    async def stop(self) -> None:
        if not self._running:
            return
        await asyncio.gather(*(ingestor.stop() for ingestor in self._ingestors))
        self._running = False

    async def health(self) -> dict[str, dict[str, str]]:
        health_data: dict[str, dict[str, str]] = {}
        for ingestor in self._ingestors:
            health_data[ingestor.metadata.name] = await ingestor.health()
        return health_data


def build_default_orchestrator(
    config: AppConfig,
    state_store: StateStore,
    event_bus: EventBus,
) -> RuntimeOrchestrator:
    ingestors: list[Ingestor] = [SystemControllerIngestor(config, state_store, event_bus)]
    if config.features.enable_esp32:
        ingestors.append(Esp32Ingestor(config, state_store, event_bus))
    if config.features.enable_antsdr:
        ingestors.append(AntsdrIngestor(config, state_store, event_bus))
    if config.features.enable_remoteid:
        ingestors.append(RemoteIdIngestor(config, state_store, event_bus))
    return RuntimeOrchestrator(ingestors)
