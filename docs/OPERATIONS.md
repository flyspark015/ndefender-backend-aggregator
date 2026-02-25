# Operations ✅

Why this exists: It is the operator handbook for production deployments, including health validation, recovery, and safe operations.

## Service Startup Checklist
- [ ] `config/default.yaml` present and validated.
- [ ] System Controller reachable at configured base URL.
- [ ] AntSDR JSONL path accessible and writable.
- [ ] RemoteID JSONL path accessible and writable.
- [ ] ESP32 device detected under `/dev/serial/by-id`.

## Health Validation Checklist
- [ ] `GET /api/v1/health` returns ok.
- [ ] `GET /api/v1/status` returns snapshot with timestamp.
- [ ] `GET /api/v1/contacts` returns list (may be empty).
- [ ] WS `/api/v1/ws` streams events.

## Subsystem Feeds (Aggregator)
- System Controller -> `/api/v1/status` (power/network/audio/system/services).
- UPS HAT E (local fallback) -> I2C bus 1 addr 0x2d (power section if controller data is empty).
- AntSDR -> JSONL tailer at `/opt/ndefender/logs/antsdr_scan.jsonl` (rf + RF contacts).
- RemoteID -> JSONL tailer at `/opt/ndefender/logs/remoteid_engine.jsonl` (remote_id + contacts).
- ESP32 -> serial telemetry (vrx/fpv/video). If missing, vrx.sys.status="DISCONNECTED" and last_error is populated.

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
  - UPS fallback still attempts to read local I2C telemetry even if controller is offline.

## Troubleshooting Degraded States
- `RF_SCAN_OFFLINE`: AntSDR scan JSONL not updating.
  - Check AntSDR reachability (default `192.168.10.2`) and `journalctl -u ndefender-rfscan -n 200 --no-pager`.
- `no_remoteid_events`: RemoteID engine is running but no frames are captured.
  - Check monitor interface (`mon0`) and `journalctl -u ndefender-remoteid-engine -n 200 --no-pager`.
- `VRX DISCONNECTED`: ESP32 serial device not detected.
  - Verify USB device under `/dev/serial/by-id` and update `config/default.yaml` if port changed.
- `UPS fallback`: Power data is taken from local I2C UPS HAT E when system-controller lacks `/api/v1/ups`.
  - Ensure I2C bus 1 device `0x2d` is present (`sudo i2cdetect -y -r 1 0x2d 0x2d`).

## RemoteID Stale / Replay Detection
- If `replay.active=false`, RemoteID contacts older than 15s are dropped and test markers (`TestDrone`, `WARMSTART`) are filtered.
- If you still see stale RemoteID timestamps, confirm RemoteID JSONL is live and not replaying.
- Logs to check:
  - `journalctl -u ndefender-remoteid-engine -n 200 --no-pager | grep -i tshark`
  - Verify monitor interface (`mon0`) is present and captures are fresh.

## RF Scan Offline Detection
- If AntSDR is disconnected or its IP is unreachable, RF scan will restart and the JSONL file will not update.
- Aggregator marks RF as offline/stale when no new JSONL events arrive.
- Logs to check:
  - `journalctl -u ndefender-rfscan -n 200 --no-pager | grep -i \"no device\"`
  - `ping -c 1 192.168.10.2` (AntSDR default IP).

## Rate Limit Exceeded Handling
- Command endpoints return `429` on excessive calls.
- Wait for cooldown window to expire.

## Safe Reboot Flow
1. Ensure `allow_unsafe_operations=true` in config.
2. Issue command with `confirm=true`.
3. Observe `COMMAND_ACK` in WS stream.
