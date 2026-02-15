# Operations ✅

Why this exists: It is the operator handbook for production deployments, including health validation, recovery, and safe operations.

## Service Startup Checklist
- [ ] `config/default.yaml` present and validated.
- [ ] API key distributed to GUI clients.
- [ ] System Controller reachable at configured base URL.
- [ ] AntSDR JSONL path accessible and writable.
- [ ] RemoteID JSONL path accessible and writable.
- [ ] ESP32 device detected under `/dev/serial/by-id`.

## Health Validation Checklist
- [ ] `GET /api/v1/health` returns ok.
- [ ] `GET /api/v1/status` returns snapshot with timestamp.
- [ ] `GET /api/v1/contacts` returns list (may be empty).
- [ ] WS `/api/v1/ws` streams events.

## Log Inspection Commands
```bash
journalctl -u ndefender-backend-aggregator -f
ls -lah /opt/ndefender/logs/
```

## JSONL Corruption Recovery
1. Stop aggregator service.
2. Move corrupted JSONL aside:
   ```bash
   mv /opt/ndefender/logs/antsdr_engine.jsonl /opt/ndefender/logs/antsdr_engine.jsonl.bad
   ```
3. Restart subsystem engine to re-create JSONL.
4. Restart aggregator.

## ESP32 Reconnect Handling
- Serial loop auto-reconnects every `reconnect_delay_seconds`.
- If no telemetry appears, verify USB cable and `/dev/serial/by-id`.

## System Controller Unreachable Behavior
- Poller marks status as degraded but API remains available.
- `system`/`power`/`network`/`audio` fields may be stale or empty.

## Rate Limit Exceeded Handling
- Command endpoints return `429` on excessive calls.
- Wait for cooldown window to expire.

## Safe Reboot Flow
1. Ensure `allow_unsafe_operations=true` in config.
2. Issue command with `confirm=true` and admin role.
3. Observe `COMMAND_ACK` in WS stream.

