# Architecture 🧭

Why this exists: It documents subsystem interactions, data flow, and failure isolation so future engineers can safely extend the platform.

## Full Subsystem Interaction Diagram

```
             ┌────────────────────────────┐
             │  N-Defender GUI / Operator │
             └──────────────┬─────────────┘
                            │
                            ▼
                ┌────────────────────┐
                │ Backend Aggregator │
                └───────┬────────────┘
                        │
        ┌───────────────┼────────────────┬────────────────┐
        ▼               ▼                ▼                ▼
   AntSDR JSONL     RemoteID JSONL   ESP32 Serial     System Controller REST
        │               │                │                │
        ▼               ▼                ▼                ▼
   RF_CONTACT_*    CONTACT_* /      ESP32_TELEMETRY   SYSTEM/UPS/NET/AUDIO
                   TELEMETRY_UPDATE     COMMAND_ACK     updates
```

## Event Flow 🔄
JSONL → Ingest → State → WS

```
JSONL/Serial/REST
      │
      ▼
 Ingestors (tail/poll/serial)
      │
      ▼
 State Store (canonical snapshot)
      │
      ├── REST snapshot (/api/v1/status)
      └── WS updates (/api/v1/ws)
```

## Command Flow 🔁
REST → Router → Subsystem → ACK → WS

```
REST /api/v1/command
      │
      ▼
 Command Router
      │
      ├─ ESP32 Handler → Serial → command_ack → WS COMMAND_ACK
      └─ System Handler → REST → ACK → WS COMMAND_ACK
```

## Failure Isolation Strategy
- Each ingestor runs independently; failure in one does not stop the API.
- JSONL tailers are restart-safe (inode change + truncation safe).
- Serial loop auto-reconnects to ESP32.
- System controller polling failure degrades gracefully with health metadata.

## Backpressure Strategy
- Internal EventBus uses bounded queues and drop‑oldest behavior to prevent lockups.
- WS broadcast is decoupled from ingestion to avoid cascade failures.

## Threading / Async Model
- FastAPI async runtime with asyncio event loop.
- Ingestors use async tasks; blocking I/O is executed with `asyncio.to_thread`.
- JSONL tailers are poll-based for predictable CPU load.

## Why JSONL Is Ground Truth
- Append-only logs provide durability across restarts.
- Aggregator can reconstruct state from log history after reboot.
- Rotation-safe tailing ensures continuity without data loss.

