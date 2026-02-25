# API Contract 📡

Why this exists: It defines the production REST + WebSocket surface consumed by the GUI and tooling, preventing drift across releases.

## Base
- `/api/v1`

## Auth 🔐
- No auth headers are required in the current deployment.

## REST Endpoints

### Health & Status
- `GET /health`
- `GET /status`

Example:
```bash
curl http://127.0.0.1:8001/api/v1/status
```

StatusSnapshot contract notes:
- Always includes stable keys (no empty top-level objects): `system`, `power`, `rf`, `remote_id`, `vrx`, `fpv`, `video`, `services`, `network`, `audio`, `contacts`, `replay`, `overall_ok`, `timestamp_ms`.
- Nulls are allowed when a subsystem is missing.
- `timestamp_ms` is epoch milliseconds.
- `replay.active=false` suppresses replay/test contacts (e.g., `TestDrone`, `WARMSTART`).

### Contacts & Telemetry
- `GET /contacts`
- `GET /system`
- `GET /power`
- `GET /rf`
- `GET /video`
- `GET /services`
- `GET /network`
- `GET /audio`

Example response excerpt (contacts):
```json
{
  "contacts": [
    {"id": "rf:5658", "type": "RF", "last_seen_ts": 123456789, "severity": "high"}
  ]
}
```

### Commands
- `POST /vrx/tune`
- `POST /scan/start`
- `POST /scan/stop`
- `POST /video/select`
- `POST /system/reboot` (confirm required + unsafe toggle)
- `POST /system/shutdown` (confirm required + unsafe toggle)

Note: If command endpoints are disabled in production, they may return `405` and no auth is enforced.

Example:
```bash
curl -X POST http://127.0.0.1:8001/api/v1/vrx/tune \
  -d '{"payload":{"vrx_id":1,"freq_hz":5740000000}}'
```

Example (unsafe):
```bash
curl -X POST http://127.0.0.1:8001/api/v1/system/reboot \
  -d '{"confirm":true}'
```

## WebSocket
- `WS /ws`

### Envelope
```json
{
  "type": "EVENT_TYPE",
  "timestamp_ms": 1700000000000,
  "source": "backend",
  "data": {}
}
```

### Event Types (Grouped)

**System**
- `SYSTEM_STATUS`
- `SYSTEM_UPDATE`
- `UPS_UPDATE`
- `NETWORK_UPDATE`
- `AUDIO_UPDATE`

**Contacts**
- `CONTACT_NEW`
- `CONTACT_UPDATE`
- `CONTACT_LOST`
- `RF_CONTACT_NEW`
- `RF_CONTACT_UPDATE`
- `RF_CONTACT_LOST`

**Telemetry**
- `TELEMETRY_UPDATE`
- `REPLAY_STATE`
- `ESP32_TELEMETRY`

**Commands & Logs**
- `COMMAND_ACK`
- `LOG_EVENT`

## Command Flow with ACK
1. Client sends REST command.
2. Router dispatches to subsystem.
3. Subsystem emits `COMMAND_ACK`.

ACK example:
```json
{
  "type": "COMMAND_ACK",
  "timestamp_ms": 1700000000000,
  "source": "esp32",
  "data": {"id":"123","ok":true,"err":null,"data":{"cmd":"SET_VRX_FREQ"}}
}
```

## Access Notes
- All endpoints are callable without auth headers.
- Unsafe actions still require `confirm=true` and config enablement.
