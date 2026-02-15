import asyncio

from ndefender_backend_aggregator.bus import EventBus
from ndefender_backend_aggregator.config import get_config
from ndefender_backend_aggregator.integrations import (
    AntsdrIngestor,
    Esp32Ingestor,
    RemoteIdIngestor,
    SystemControllerIngestor,
)
from ndefender_backend_aggregator.state import StateStore


def test_integration_stubs_health():
    config = get_config()
    state_store = StateStore()
    event_bus = EventBus()
    ingestors = [
        AntsdrIngestor(config, state_store, event_bus),
        Esp32Ingestor(config, state_store, event_bus),
        RemoteIdIngestor(config, state_store, event_bus),
        SystemControllerIngestor(config, state_store, event_bus),
    ]

    async def run() -> None:
        for ingestor in ingestors:
            await ingestor.start()
            health = await ingestor.health()
            assert "status" in health
            await ingestor.stop()

    asyncio.run(run())
