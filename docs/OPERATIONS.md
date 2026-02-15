# Operations ✅

Why this exists: It provides a production checklist and operational procedures for stable deployment and safe recovery.

## Pre-Flight Checklist
- [ ] Configuration file present and validated.
- [ ] API key set and distributed to GUI clients.
- [ ] System Controller reachable at configured base URL.
- [ ] AntSDR JSONL path accessible.
- [ ] RemoteID JSONL path accessible.
- [ ] ESP32 serial device detected.

## Runtime Health
- `GET /api/v1/health` returns ok.
- `GET /api/v1/status` returns latest snapshot.
- WebSocket `/api/v1/ws` streams `SYSTEM_UPDATE` events.

## Safety Controls
- Unsafe operations disabled by default.
- Reboot/shutdown require `confirm=true`.
- Rate limits enabled on command endpoints.

## Recovery Steps
1. Restart service via systemd.
2. Verify JSONL tailers reattach (no data loss).
3. Confirm ESP32 telemetry resuming.
4. Re-run WS contract check on recent logs.

## WS Contract Check
Run the validator on any JSONL or captured WS stream:

```bash
python3 tools/ws_contract_check.py /opt/ndefender/logs/*.jsonl
```

