import asyncio

from ndefender_backend_aggregator.ingest.contracts import Ingestor, IngestorMetadata
from ndefender_backend_aggregator.models import EventEnvelope


class StubIngestor(Ingestor):
    def __init__(self) -> None:
        self.metadata = IngestorMetadata(name="stub", source="test")
        self.started = False

    async def start(self) -> None:
        self.started = True

    async def stop(self) -> None:
        self.started = False

    async def health(self) -> dict[str, str]:
        return {"status": "ok"}

    async def handle_event(self, event: EventEnvelope) -> None:
        return None


def test_ingestor_contract():
    ingestor = StubIngestor()

    async def run() -> None:
        await ingestor.start()
        assert ingestor.started is True
        await ingestor.handle_event(
            EventEnvelope(
                type="SYSTEM_UPDATE",
                timestamp_ms=1,
                source="test",
                data={},
            )
        )
        await ingestor.stop()
        assert ingestor.started is False

    asyncio.run(run())
