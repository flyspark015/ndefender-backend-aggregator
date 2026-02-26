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
- Always includes stable keys (no empty top-level objects): `system`, `power`, `rf`, `remote_id`, `gps`, `esp32`, `antsdr`, `vrx`, `fpv`, `video`, `services`, `network`, `audio`, `contacts`, `replay`, `overall_ok`, `timestamp_ms`.
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
- `GET /gps`
- `GET /esp32`
- `GET /antsdr`
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
- `POST /esp32/buzzer`
- `POST /esp32/leds`
- `POST /esp32/buttons/simulate` (local-only)
- `POST /esp32/config`
- `POST /system/reboot` (confirm required + unsafe toggle)
- `POST /system/shutdown` (confirm required + unsafe toggle)

### Proxy Controls (System Controller)
- `POST /services/{name}/restart`
- `GET /network/wifi/state`
- `GET /network/wifi/scan`
- `POST /network/wifi/enable`
- `POST /network/wifi/connect`
- `POST /network/wifi/disconnect`
- `GET /network/bluetooth/state`
- `GET /network/bluetooth/devices`
- `POST /network/bluetooth/enable`
- `POST /network/bluetooth/scan/start`
- `POST /network/bluetooth/scan/stop`
- `POST /network/bluetooth/pair`
- `POST /network/bluetooth/unpair`
- `POST /gps/restart`
- `POST /audio/mute`
- `POST /audio/volume`

### Proxy Controls (AntSDR)
- `GET /antsdr/device`
- `GET /antsdr/sweep/state`
- `GET /antsdr/gain`
- `GET /antsdr/stats`
- `POST /antsdr/sweep/start`
- `POST /antsdr/sweep/stop`
- `POST /antsdr/gain/set`
- `POST /antsdr/device/reset` (confirm required)
- `POST /antsdr/device/calibrate` (confirm required)

### Proxy Controls (RemoteID)
- `GET /remote_id/status`
- `GET /remote_id/contacts`
- `GET /remote_id/stats`
- `POST /remote_id/monitor/start`
- `POST /remote_id/monitor/stop`
- `GET /remote_id/replay/state`
- `POST /remote_id/replay/start`
- `POST /remote_id/replay/stop`

Note: If command endpoints are disabled in production, they may return `405` and no auth is enforced.

Example:
```bash
curl -X POST http://127.0.0.1:8001/api/v1/vrx/tune \
  -d '{"payload":{"vrx_id":1,"freq_hz":5740000000},"confirm":false}'
```

Example (unsafe):
```bash
curl -X POST http://127.0.0.1:8001/api/v1/system/reboot \
  -d '{"payload":{},"confirm":true}'
```

## WebSocket
- `WS /api/v1/ws`

### Envelope
```json
{
  "type": "EVENT_TYPE",
  "timestamp_ms": 1700000000000,
  "source": "aggregator",
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
