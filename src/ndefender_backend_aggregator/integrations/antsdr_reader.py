"""AntSDR JSONL reader (stub)."""

from __future__ import annotations

from ..bus import EventBus
from ..config import AppConfig
from ..ingest import Ingestor, IngestorMetadata
from ..models import EventEnvelope
from ..state import StateStore


class AntsdrIngestor(Ingestor):
    """Stub implementation for AntSDR JSONL tailing."""

    metadata = IngestorMetadata(name="antsdr", source="antsdr")

    def __init__(
        self,
        config: AppConfig | None = None,
        state_store: StateStore | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self._config = config
        self._state_store = state_store
        self._event_bus = event_bus
        self._running = False

    async def start(self) -> None:
        self._running = True

    async def stop(self) -> None:
        self._running = False

    async def health(self) -> dict[str, str]:
        return {"status": "stub", "running": str(self._running).lower()}

    async def handle_event(self, event: EventEnvelope) -> None:
        return None
