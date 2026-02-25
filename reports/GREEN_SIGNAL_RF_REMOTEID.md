# N-Defender RF + RemoteID Data Quality Report
Generated: 2026-02-25T22:28:53Z

## Summary
- RF: OFFLINE with explicit root cause (antsdr_unreachable).
- RemoteID: capture_active true (capture running), state DEGRADED due to no ODID frames.
- WS: PASS (>=3 messages).

## Evidence (Public)
### /api/v1/status
```
false
{
  "last_event": {
    "reason": "antsdr_unreachable"
  },
  "last_event_type": "RF_SCAN_OFFLINE",
  "last_timestamp_ms": 1772058533128,
  "scan_active": false,
  "status": "offline",
  "last_error": "antsdr_unreachable"
}
{
  "last_event": {
    "reason": "no_odid_frames"
  },
  "last_event_type": "REMOTEID_STALE",
  "last_timestamp_ms": 1772058530152,
  "state": "DEGRADED",
  "mode": "live",
  "capture_active": true,
  "last_error": "no_odid_frames"
}
```

### RF scan logs (last 20)
```
Feb 26 03:58:49 ndefender-pi python3[52102]: TimeoutError: [Errno 110] Connection timed out
Feb 26 03:58:49 ndefender-pi python3[52102]: During handling of the above exception, another exception occurred:
Feb 26 03:58:49 ndefender-pi python3[52102]: Traceback (most recent call last):
Feb 26 03:58:49 ndefender-pi python3[52102]:   File "/home/toybook/antsdr_scan/run.py", line 42, in <module>
Feb 26 03:58:49 ndefender-pi python3[52102]:     main()
Feb 26 03:58:49 ndefender-pi python3[52102]:   File "/home/toybook/antsdr_scan/run.py", line 18, in main
Feb 26 03:58:49 ndefender-pi python3[52102]:     radio = AntSDR(
Feb 26 03:58:49 ndefender-pi python3[52102]:             ^^^^^^^
Feb 26 03:58:49 ndefender-pi python3[52102]:   File "/home/toybook/antsdr_scan/core/radio.py", line 5, in __init__
Feb 26 03:58:49 ndefender-pi python3[52102]:     self.sdr = adi.ad9364(uri=uri)
Feb 26 03:58:49 ndefender-pi python3[52102]:                ^^^^^^^^^^^^^^^^^^^
Feb 26 03:58:49 ndefender-pi python3[52102]:   File "/home/toybook/.local/lib/python3.11/site-packages/adi/rx_tx.py", line 734, in __init__
Feb 26 03:58:49 ndefender-pi python3[52102]:     rx_def.__init__(self, *args, **kwargs)
Feb 26 03:58:49 ndefender-pi python3[52102]:   File "/home/toybook/.local/lib/python3.11/site-packages/adi/rx_tx.py", line 653, in __init__
Feb 26 03:58:49 ndefender-pi python3[52102]:     shared_def.__init__(self, *args, **kwargs)
Feb 26 03:58:49 ndefender-pi python3[52102]:   File "/home/toybook/.local/lib/python3.11/site-packages/adi/rx_tx.py", line 603, in __init__
Feb 26 03:58:49 ndefender-pi python3[52102]:     context_manager.__init__(self, uri_ctx, self._device_name)
Feb 26 03:58:49 ndefender-pi python3[52102]:   File "/home/toybook/.local/lib/python3.11/site-packages/adi/context_manager.py", line 38, in __init__
Feb 26 03:58:49 ndefender-pi python3[52102]:     raise Exception("No device found")
Feb 26 03:58:49 ndefender-pi python3[52102]: Exception: No device found
```

### RemoteID service status
```
● ndefender-remoteid-engine.service - N-Defender RemoteID Engine
     Loaded: loaded (/etc/systemd/system/ndefender-remoteid-engine.service; enabled; preset: enabled)
     Active: active (running) since Thu 2026-02-26 03:37:01 IST; 21min ago
   Main PID: 18571 (ndefender-remot)
      Tasks: 3 (limit: 19359)
        CPU: 33.771s
     CGroup: /system.slice/ndefender-remoteid-engine.service
             ├─18571 /home/toybook/Ndefender-Remoteid-Engine/.venv/bin/python /home/toybook/Ndefender-Remoteid-Engine/.venv/bin/ndefender-remoteid run --config /home/toybook/Ndefender-Remoteid-Engine/config/default.yaml
             ├─18586 tshark -i mon0 -l -T ek
             └─18629 /usr/bin/dumpcap -n -i mon0 -Z none
```

### WS public test
```
connected
first_200={"type":"HELLO","timestamp_ms":1772058536218,"source":"aggregator","data":{"timestamp_ms":1772058536218}}
received=8, first_type=HELLO
PASS: received >=3 messages
```

## Decisions
- RF uses explicit offline reason when AntSDR unreachable (`antsdr_unreachable`).
- RemoteID `capture_active` reflects capture running even when no frames are decoded (`no_odid_frames`).

## Next Actions (if hardware becomes available)
- Bring AntSDR online at `ip:192.168.10.2` and verify JSONL updates in `/opt/ndefender/logs/antsdr_scan.jsonl`.
- Verify ODID frames on `mon0` with `sudo tshark -i mon0 -a duration:5 -Y opendroneid`.
