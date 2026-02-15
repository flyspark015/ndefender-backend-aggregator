from ndefender_backend_aggregator.models import EventEnvelope, StatusSnapshot


def test_status_snapshot_defaults():
    snapshot = StatusSnapshot(
        timestamp_ms=1,
        system={},
        power={},
        rf={},
        remote_id={},
        vrx={},
        video={},
        services=[],
        network={},
        audio={},
    )
    assert snapshot.timestamp_ms == 1


def test_event_envelope():
    envelope = EventEnvelope(
        type="SYSTEM_UPDATE",
        timestamp_ms=10,
        source="aggregator",
        data={"ok": True},
    )
    assert envelope.type == "SYSTEM_UPDATE"
