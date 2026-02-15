import asyncio

from ndefender_backend_aggregator.bus import EventBus
from ndefender_backend_aggregator.config import get_config
from ndefender_backend_aggregator.runtime import build_default_orchestrator
from ndefender_backend_aggregator.state import StateStore


def test_orchestrator_start_stop():
    orchestrator = build_default_orchestrator(get_config(), StateStore(), EventBus())

    async def run() -> None:
        await orchestrator.start()
        health = await orchestrator.health()
        assert "system-controller" in health
        await orchestrator.stop()

    asyncio.run(run())
