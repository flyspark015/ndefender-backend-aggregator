# N-Defender GREEN SIGNAL LIVE DATA Report
Generated: 2026-02-26
Hostname: ndefender-pi

## Summary
| Component | Status | Evidence |
| --- | --- | --- |
| Local REST | PASS | all /api/v1 endpoints 200 |
| Public REST | PASS | all /api/v1 endpoints 200 |
| Local WS | PASS (msgs=1) | SYSTEM_UPDATE received |
| Public WS | FAIL (msgs=1) | expected >=3 messages in 10s |
| CORS | FAIL | OPTIONS returned 200 but missing allow-origin/headers |
| Status Sections | PASS | power/rf/remote_id/vrx/fpv/video present + explicit states |

## REST (Local)
| Endpoint | HTTP | JSON |
| --- | --- | --- |
| /health | 200 | True |
| /status | 200 | True |
| /contacts | 200 | True |
| /system | 200 | True |
| /power | 200 | True |
| /rf | 200 | True |
| /video | 200 | True |
| /services | 200 | True |
| /network | 200 | True |
| /audio | 200 | True |

## REST (Public)
| Endpoint | HTTP | JSON |
| --- | --- | --- |
| /health | 200 | True |
| /status | 200 | True |
| /contacts | 200 | True |
| /system | 200 | True |
| /power | 200 | True |
| /rf | 200 | True |
| /video | 200 | True |
| /services | 200 | True |
| /network | 200 | True |
| /audio | 200 | True |

## WebSocket
| Target | connect_ok | msgs_received | first_type | first_200 |
| --- | --- | --- | --- | --- |
| Local | True | 1 | SYSTEM_UPDATE | {"type":"SYSTEM_UPDATE","timestamp_ms":1772054048895,... |
| Public | True | 1 | SYSTEM_UPDATE | {"type":"SYSTEM_UPDATE","timestamp_ms":1772054025851,... |

## Key Section Checks (/status)
All sections are present and not empty dicts. When degraded, explicit status/error fields are present.

Evidence snippet (local):
```
"power":{"pack_voltage_v":16.71,"soc_percent":98,"state":"IDLE","status":"ok"}
"rf":{"last_event_type":"RF_SCAN_OFFLINE","scan_active":false}
"remote_id":{"state":"DEGRADED","last_error":"no_remoteid_events"}
"vrx":{"sys":{"status":"DISCONNECTED","last_error":".../dev/ttyACM0"}}
```

## CORS
OPTIONS checks returned 200 but missing allow-origin/allow-headers. This fails strict CORS requirements for browser clients.

## Verdict
RED SIGNAL
Reason: Public WS capture produced only 1 message (requirement >=3 in 10s). CORS headers missing.

## Next Actions
1. Fix WS message cadence to ensure >=3 messages in 10s.
2. Ensure OPTIONS responses include Access-Control-Allow-Origin/Methods/Headers.
3. Re-run GREEN SIGNAL after fixes.
