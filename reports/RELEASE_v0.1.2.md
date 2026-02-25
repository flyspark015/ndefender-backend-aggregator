# Release v0.1.2 - live-data-green

## Changes
- WS heartbeat + HELLO for deterministic >=3 msgs/10s.
- CORS set to `*` with GET/POST/OPTIONS and `allow-headers=*`.
- GREEN SIGNAL checks made strict (CORS headers + WS message count).

## Evidence
- WS (public): `received=8, first_type=HELLO`
- CORS preflight: `access-control-allow-origin: *`, `allow-methods: GET, POST, OPTIONS`
- Report: `reports/README_GREEN_SIGNAL.md` (Conclusion: GREEN SIGNAL)

## Notes
- RemoteID engine still degraded; surfaced explicitly in `/status`.
- ESP32 not connected; `vrx.sys.status=DISCONNECTED`.
