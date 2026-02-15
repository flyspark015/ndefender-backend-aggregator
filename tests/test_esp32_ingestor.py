import asyncio

from ndefender_backend_aggregator.bus import EventBus
from ndefender_backend_aggregator.config import get_config
from ndefender_backend_aggregator.contacts import ContactStore
from ndefender_backend_aggregator.integrations.esp32_serial import Esp32Ingestor
from ndefender_backend_aggregator.state import StateStore


def test_esp32_telemetry_updates_state():
    expected_video = 2
    config = get_config()
    state_store = StateStore()
    event_bus = EventBus()
    ingestor = Esp32Ingestor(config, state_store, event_bus, ContactStore(state_store))

    telemetry = {
        "type": "telemetry",
        "timestamp_ms": 1000,
        "sel": 1,
        "vrx": [{"id": 1, "freq_hz": 5740000000, "rssi_raw": 200}],
        "video": {"selected": 2},
        "led": {"r": 0, "y": 1, "g": 0},
        "sys": {"uptime_ms": 1000, "heap": 123456},
    }

    async def run() -> None:
        queue = await event_bus.subscribe()
        await ingestor._handle_message(telemetry)
        snapshot = await state_store.snapshot()
        assert snapshot.vrx["selected"] == 1
        assert snapshot.video["selected"] == expected_video
        event = await queue.get()
        assert event.type == "ESP32_TELEMETRY"

    asyncio.run(run())


def test_esp32_command_ack_resolves_future():
    config = get_config()
    state_store = StateStore()
    event_bus = EventBus()
    ingestor = Esp32Ingestor(config, state_store, event_bus, ContactStore(state_store))

    async def run() -> None:
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        ingestor._pending["abc"] = future
        await ingestor._handle_message(
            {
                "type": "command_ack",
                "timestamp_ms": 1234,
                "id": "abc",
                "ok": True,
                "err": None,
                "data": {"cmd": "SET_VRX_FREQ"},
            }
        )
        assert future.done()

    asyncio.run(run())
