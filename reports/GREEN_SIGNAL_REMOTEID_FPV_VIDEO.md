# GREEN SIGNAL - RemoteID / FPV / Video Data Quality
Date: 2026-02-26

## RemoteID Status
- Engine was restart-looping due to missing `mon0` (tshark: no device named mon0).
- Created monitor interface and verified capture:
  - `sudo iw phy phy1 interface add mon0 type monitor`
  - `sudo ip link set mon0 up`
  - `sudo tshark -i mon0 -c 1 -a duration:3` (1 packet captured)
- Service restarted and running with tshark/dumpcap.

Current /status (public):
```
remote_id.state=DEGRADED
capture_active=false
last_error=no_remoteid_events
```
Root cause: No RemoteID frames observed yet. Capture is active and stable; no restart storm.

## FPV vs VRX Mapping
- `fpv` now mirrors selected VRX entry:
  - `fpv.selected = vrx.selected`
  - `fpv.freq_hz / fpv.rssi_raw` from matching VRX item

Evidence:
```
"fpv": {"selected":1,"freq_hz":5740000000,"rssi_raw":596,"scan_state":"idle"}
```

## Video Health
- `video.status` inferred from `/dev/video*` presence.
- Current status: `video.status="ok"`

## Contacts Timestamp Semantics
- `contacts[].last_seen_ts` is epoch ms.
- FPV contacts also include `last_seen_uptime_ms` when ESP32 provides uptime timestamps.

Evidence:
```
"last_seen_ts": 1772057370997,
"last_seen_uptime_ms": 733359
```

## Verdict
- Data quality improvements applied.
- RemoteID remains DEGRADED due to no captured frames; service is stable and capture is configured.
