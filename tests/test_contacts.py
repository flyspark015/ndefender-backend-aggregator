import asyncio

from ndefender_backend_aggregator.contacts import ContactStore
from ndefender_backend_aggregator.state import StateStore


def test_contact_store_merges_and_sorts():
    expected_count = 2
    state_store = StateStore()
    store = ContactStore(state_store)

    async def run() -> None:
        await store.update_remoteid(
            "CONTACT_NEW",
            {"id": "r1", "type": "REMOTE_ID", "last_seen_ts": 10},
            10,
        )
        await store.update_rf(
            "RF_CONTACT_NEW",
            {"id": "rf1", "confidence": 0.9},
            20,
        )
        snapshot = await state_store.snapshot()
        assert len(snapshot.contacts) == expected_count
        assert snapshot.contacts[0]["id"] == "rf1"

    asyncio.run(run())
