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
- [ ] `GET /api/v1/status` returns snapshot with `timestamp_ms`.
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

## FPV Field Semantics
- `fpv` is mirrored from the selected VRX entry when available:
  - `fpv.selected` = `vrx.selected`
  - `fpv.freq_hz` / `fpv.rssi_raw` from the matching `vrx` entry.
- If no VRX selection exists, `fpv` remains default/idle.

## Video Health Probe
- `video.status` is inferred by device presence:
  - `ok` if `/dev/video*` exists.
  - `offline` if no video device present.

## Contact Timestamp Semantics
- `contacts[].last_seen_ts` is epoch milliseconds.
- For ESP32 FPV contacts, if device reports uptime-based timestamps, they are stored in `last_seen_uptime_ms` and `last_seen_ts` is converted to epoch.

## System Controller Unreachable Behavior
- Poller marks status as degraded but API remains available.
- `system`/`power`/`network`/`audio` fields may be stale or empty.
  - UPS fallback still attempts to read local I2C telemetry even if controller is offline.

## Troubleshooting Degraded States
- `RF_SCAN_OFFLINE`: AntSDR scan JSONL not updating.
  - If `last_error=antsdr_unreachable`, verify AntSDR IP (default `192.168.10.2`) and `journalctl -u ndefender-rfscan -n 200 --no-pager`.
  - If `last_error=rf_jsonl_missing`, confirm JSONL path `/opt/ndefender/logs/antsdr_scan.jsonl` is writable.
- `REMOTEID_STALE` with `last_error=no_odid_frames`: capture is running but no OpenDroneID frames decoded.
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

## RemoteID capture_active Semantics
- `capture_active=true` means the capture process is running (tshark active, interface present), even if 0 frames are decoded.
- `capture_active=false` means capture is not running or the interface is missing/down.
- `last_error` clarifies why no events are present:
  - `no_odid_frames`: capture running, no decoded frames.
  - `mon0_missing` / `mon0_down`: monitor interface not ready.
  - `remoteid_service_inactive`: engine not running.

## RF Scan (AntSDR) — Offline / Restart Storm
### Meaning of `rf.status` + `last_error`
- `antsdr_unreachable`: AntSDR IP not reachable (radio not powered, wrong IP, or link down).
- `rf_jsonl_missing`: JSONL file missing or not writable.
- `no_recent_rf_events`: JSONL exists but no new events within TTL.

### Diagnostics (copy/paste)
```bash
journalctl -u ndefender-rfscan -n 200 --no-pager
ip a
ping -c 1 -W 1 192.168.10.2 || true
tail -n 3 /opt/ndefender/logs/antsdr_scan.jsonl || true
```

### What “No device found” means
- AntSDR is not powered.
- AntSDR is on a different IP/subnet than configured.
- Ethernet is not connected to the AntSDR network.

### Recovery checklist
1. Verify AntSDR power and link LEDs.
2. Confirm you are on the AntSDR subnet (e.g., `192.168.10.x`).
3. Update AntSDR IP in `/home/toybook/antsdr_scan/config.yaml` if needed.
4. Restart rfscan (after fixing connectivity):
   ```bash
   sudo systemctl restart ndefender-rfscan
   ```

### Restart storm control
- The service uses backoff via systemd to avoid rapid restarts:
  - `RestartSec=5`
  - `StartLimitIntervalSec=60`
  - `StartLimitBurst=6`

## RemoteID — capture_active vs decoded frames
- `capture_active=true` means tshark is running and `mon0` exists.
- `last_error=no_odid_frames` means no OpenDroneID frames observed yet.
- You will not see RemoteID unless a nearby drone is broadcasting ODID.

### Minimum verification commands
```bash
ip link show mon0 || true
sudo tshark -i mon0 -a duration:5 -c 20
sudo tshark -i mon0 -a duration:8 -Y opendroneid -T fields -e OpenDroneID.basicID_id_asc 2>/dev/null | head
```

## overall_ok Semantics
- `overall_ok` stays `false` if any subsystem is `DEGRADED` or `OFFLINE`.
- In lab conditions, it is acceptable for `rf` or `remote_id` to be degraded if hardware is absent.

## RemoteID Engine Bring-Up
- RemoteID capture requires a monitor-mode interface (`mon0`).
- If `tshark` reports `There is no device named "mon0"`:
  - Create monitor interface on a phy that supports monitor (example for `wlan0` / phy1):
    - `sudo iw phy phy1 interface add mon0 type monitor`
    - `sudo ip link set mon0 up`
  - Verify `tshark` can capture: `sudo tshark -i mon0 -c 1 -a duration:3`
  - Restart service: `sudo systemctl restart ndefender-remoteid-engine`

## RF Scan Offline Detection
- If AntSDR is disconnected or its IP is unreachable, RF scan will restart and the JSONL file will not update.
- Aggregator marks RF as offline/stale when no new JSONL events arrive and sets:
  - `status=offline`
  - `last_error=antsdr_unreachable` (or `rf_jsonl_missing`)
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
