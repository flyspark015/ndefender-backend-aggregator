# Integration Guide 🔌

Why this exists: It documents how each subsystem is ingested and normalized so changes can be coordinated safely.

## System Controller
- Polled via REST for UPS, network, audio, and service status.
- Optional WS subscription if available.

## ESP32 Panel
- Serial newline JSON at 115200 baud.
- Telemetry and command acknowledgments are normalized into the state store.

## AntSDR Scan Engine
- JSONL ground-truth feed for RF detections.
- Rotation-safe tailing required for reliability.

## RemoteID Engine
- JSONL feed for RemoteID contact updates.
- Timestamp normalization to `timestamp_ms` required.

