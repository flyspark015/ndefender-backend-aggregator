# Integration Guide 🔌

Why this exists: It documents how each subsystem is ingested and normalized so changes can be coordinated safely.

## System Controller
- Polled via REST for UPS, network, audio, and service status.
- Optional WS subscription if available.
 - Currently implemented via REST polling.

## ESP32 Panel
- Serial newline JSON at 115200 baud.
- Telemetry and command acknowledgments are normalized into the state store.
 - Commands are routed using the ESP32 command handler.

## AntSDR Scan Engine
- JSONL ground-truth feed for RF detections.
- Rotation-safe tailing required for reliability.
 - Events normalized to RF_CONTACT_* types.

## RemoteID Engine
- JSONL feed for RemoteID contact updates.
- Timestamp normalization to `timestamp_ms` required.

## Contracts
See `docs/INTEGRATION_CONTRACTS.md` for the ingestion interface and event envelope requirements.

## Stub Status
All integration modules are currently stubs and implement the ingestion interface without runtime wiring.
