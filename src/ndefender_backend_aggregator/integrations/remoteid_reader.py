"""RemoteID JSONL reader (stub)."""

from __future__ import annotations

from ..ingest import Ingestor, IngestorMetadata
from ..models import EventEnvelope


class RemoteIdIngestor(Ingestor):
    """Stub implementation for RemoteID JSONL tailing."""

    metadata = IngestorMetadata(name="remoteid", source="remoteid")

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
