import asyncio
import json
from pathlib import Path

import pytest

from ndefender_backend_aggregator.bus import EventBus
from ndefender_backend_aggregator.config import get_config
from ndefender_backend_aggregator.ingest.antsdr_ingest import AntsdrIngestor
from ndefender_backend_aggregator.state import StateStore


@pytest.mark.asyncio
async def test_antsdr_ingest_emits_event(tmp_path: Path):
    config = get_config()
    config.antsdr.jsonl_path = str(tmp_path / "antsdr.jsonl")
    config.antsdr.tail_poll_interval_ms = 10
    path = Path(config.antsdr.jsonl_path)
    path.write_text(json.dumps({"type": "CONTACT_NEW", "timestamp": 1, "data": {"id": "x"}}) + "\n")

    state_store = StateStore()
    event_bus = EventBus()
    ingestor = AntsdrIngestor(config, state_store, event_bus)

    queue = await event_bus.subscribe()

    await ingestor.start()
    await asyncio.sleep(0.05)
    await ingestor.stop()

    event = await queue.get()
    assert event.type == "RF_CONTACT_NEW"
    assert event.data == {"id": "x"}
