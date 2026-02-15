"""System Controller integration (stub)."""

from __future__ import annotations

from ..ingest import Ingestor, IngestorMetadata
from ..models import EventEnvelope


class SystemControllerIngestor(Ingestor):
    """Stub implementation for System Controller polling."""

    metadata = IngestorMetadata(name="system-controller", source="system")

    def __init__(self) -> None:
        self._running = False

    async def start(self) -> None:
        self._running = True

    async def stop(self) -> None:
        self._running = False

    async def health(self) -> dict[str, str]:
        return {"status": "stub", "running": str(self._running).lower()}

    async def handle_event(self, event: EventEnvelope) -> None:
        return None
