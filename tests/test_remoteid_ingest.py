import asyncio
import json
from pathlib import Path

import pytest

from ndefender_backend_aggregator.bus import EventBus
from ndefender_backend_aggregator.config import get_config
from ndefender_backend_aggregator.contacts import ContactStore
from ndefender_backend_aggregator.ingest.remoteid_ingest import RemoteIdIngestor
from ndefender_backend_aggregator.state import StateStore


@pytest.mark.asyncio
async def test_remoteid_ingest_emits_event(tmp_path: Path):
    config = get_config()
    config.remoteid.jsonl_path = str(tmp_path / "remoteid.jsonl")
    config.remoteid.tail_poll_interval_ms = 10
    path = Path(config.remoteid.jsonl_path)
    path.write_text(
        json.dumps(
            {
                "type": "CONTACT_NEW",
                "timestamp": 1,
                "source": "remoteid",
                "data": {"id": "r1", "type": "REMOTE_ID", "last_seen_ts": 1},
            }
        )
        + "\n"
    )

    state_store = StateStore()
    event_bus = EventBus()
    ingestor = RemoteIdIngestor(config, state_store, event_bus, ContactStore(state_store))

    queue = await event_bus.subscribe()

    await ingestor.start()
    await asyncio.sleep(0.05)
    await ingestor.stop()

    event = await queue.get()
    assert event.type == "CONTACT_NEW"
    assert event.data["id"] == "r1"
