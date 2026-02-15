# Integration Contracts 📜

Why this exists: It defines the strict interface between ingestion modules and the core runtime so integrations can be implemented without API drift.

## Ingestor Base Contract
All ingestion modules implement the `Ingestor` interface.

### Responsibilities
- **start**: Begin the ingestion loop (tailer/poller/serial reader).
- **stop**: Stop the loop cleanly for shutdown or restart.
- **health**: Report minimal health metadata for observability.
- **handle_event**: Accept normalized `EventEnvelope` objects.

### Metadata
Each ingestor declares immutable `IngestorMetadata` with:
- `name`: Human-friendly name.
- `source`: Canonical source identifier (e.g., `system`, `esp32`).
- `enabled`: Gate for feature flags and configuration.

## Event Envelope
All ingestion events use the canonical `EventEnvelope` model:

```json
{
  "type": "EVENT_TYPE",
  "timestamp_ms": 123456,
  "source": "subsystem",
  "data": {}
}
```

## Reliability Expectations
- Ingestors must be restart-safe.
- Partial failures must not crash the API.
- Slow or stalled ingestion must not block other modules.

