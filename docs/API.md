# API Contract 📡

Why this exists: It defines the public surface consumed by the GUI and tooling, preventing drift across releases.

## Base
- `/api/v1`

## Auth
- All endpoints require `X-API-Key` unless explicitly disabled in configuration.
- RBAC is enforced via `X-Role` when enabled.

## REST Endpoints
- `GET /health`: Liveness/readiness check.
- `GET /status`: Full canonical snapshot.
- `GET /contacts`: Unified contacts list.
- `GET /system`: System stats from controller.
- `GET /power`: UPS/power status.
- `GET /rf`: RF scan status.
- `GET /video`: Video/VRX status.
- `GET /services`: Service supervision status.
- `GET /network`: Network status.
- `GET /audio`: Audio status.

## Command Endpoints
- `POST /vrx/tune`
- `POST /scan/start`
- `POST /scan/stop`
- `POST /video/select`
- `POST /system/reboot`
- `POST /system/shutdown`

Command routing details live in `docs/COMMANDS.md`.

## WebSocket
- `WS /ws` (full path: `/api/v1/ws`)

### Envelope
```json
{
  "type": "CONTACT_UPDATE | SYSTEM_UPDATE | POWER_UPDATE | RF_UPDATE | COMMAND_ACK",
  "timestamp_ms": 123456,
  "source": "aggregator",
  "data": {}
}
```
