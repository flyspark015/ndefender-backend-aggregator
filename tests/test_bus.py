import asyncio

from ndefender_backend_aggregator.bus import EventBus
from ndefender_backend_aggregator.models import EventEnvelope


def test_event_bus_publish_delivers():
    bus = EventBus(max_queue_size=2)
    event = EventEnvelope(
        type="SYSTEM_UPDATE",
        timestamp_ms=1,
        source="aggregator",
        data={"ok": True},
    )

    async def run() -> None:
        queue = await bus.subscribe()
        await bus.publish(event)
        received = await queue.get()
        assert received.model_dump() == event.model_dump()

    asyncio.run(run())


def test_event_bus_drops_oldest_when_full():
    expected_seq = 2
    bus = EventBus(max_queue_size=1)
    first = EventEnvelope(
        type="SYSTEM_UPDATE",
        timestamp_ms=1,
        source="aggregator",
        data={"seq": 1},
    )
    second = EventEnvelope(
        type="SYSTEM_UPDATE",
        timestamp_ms=2,
        source="aggregator",
        data={"seq": 2},
    )

    async def run() -> None:
        queue = await bus.subscribe()
        await bus.publish(first)
        await bus.publish(second)
        received = await queue.get()
        assert received.data["seq"] == expected_seq

    asyncio.run(run())
