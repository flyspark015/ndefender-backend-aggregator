"""Contracts for ingestion modules."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..models import EventEnvelope


@dataclass(frozen=True)
class IngestorMetadata:
    name: str
    source: str
    enabled: bool = True


class Ingestor(ABC):
    """Base class for ingestion modules."""

    metadata: IngestorMetadata

    @abstractmethod
    async def start(self) -> None:
        """Begin ingestion loop."""

    @abstractmethod
    async def stop(self) -> None:
        """Stop ingestion loop."""

    @abstractmethod
    async def health(self) -> dict[str, str]:
        """Return minimal health state for monitoring."""

    @abstractmethod
    async def handle_event(self, event: EventEnvelope) -> None:
        """Handle a normalized event."""
