# N-Defender GREEN SIGNAL LIVE DATA Report (v2)
Generated: 2026-02-26
Hostname: ndefender-pi

## Summary
| Component | Status | Evidence |
| --- | --- | --- |
| Local REST | PASS | all /api/v1 endpoints 200 |
| Public REST | PASS | all /api/v1 endpoints 200 |
| Local WS | PASS | msgs_received=7 |
| Public WS | PASS | msgs_received=7 |
| CORS | PASS | allow-origin=* allow-methods=GET, POST, OPTIONS |
| Status Sections | PASS | no {} blocks; explicit degraded states when needed |

## Evidence Snippets
Local `/status` (selected sections):
```
"power":{"pack_voltage_v":16.709,"soc_percent":98,"state":"IDLE","status":"ok"}
"rf":{"last_event_type":"RF_CONTACT_UPDATE","last_timestamp_ms":1772054815...}
"remote_id":{"state":"DEGRADED","last_error":"no_remoteid_events"}
"vrx":{"sys":{"status":"DISCONNECTED","last_error":".../dev/ttyACM0"}}
```
Public WS:
```
connected
received=7, first_type=HELLO
```
CORS preflight (public):
```
access-control-allow-origin: *
access-control-allow-methods: GET, POST, OPTIONS
```

## Notes
- RemoteID engine still degraded (no live frames) but explicitly surfaced in `/status`.
- ESP32 device not connected; `vrx.sys.status=DISCONNECTED` with `last_error` populated.

## Verdict
GREEN SIGNAL (criteria met: public+local REST/WS/CORS pass; /status has no {} blocks)
