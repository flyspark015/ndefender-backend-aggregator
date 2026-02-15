import asyncio

from ndefender_backend_aggregator.config import get_config
from ndefender_backend_aggregator.runtime import build_default_orchestrator


def test_orchestrator_start_stop():
    orchestrator = build_default_orchestrator(get_config())

    async def run() -> None:
        await orchestrator.start()
        health = await orchestrator.health()
        assert "system-controller" in health
        await orchestrator.stop()

    asyncio.run(run())
