import asyncio

from ndefender_backend_aggregator.integrations import (
    AntsdrIngestor,
    Esp32Ingestor,
    RemoteIdIngestor,
    SystemControllerIngestor,
)


def test_integration_stubs_health():
    ingestors = [
        AntsdrIngestor(),
        Esp32Ingestor(),
        RemoteIdIngestor(),
        SystemControllerIngestor(),
    ]

    async def run() -> None:
        for ingestor in ingestors:
            await ingestor.start()
            health = await ingestor.health()
            assert health["status"] == "stub"
            await ingestor.stop()

    asyncio.run(run())
