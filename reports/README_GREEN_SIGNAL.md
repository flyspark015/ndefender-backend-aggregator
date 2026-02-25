# N-Defender GREEN SIGNAL Report
Generated: 2026-02-25T22:11:02Z
Hostname: ndefender-pi

## Summary
| Component | Status | Evidence |
| --- | --- | --- |
| Local REST | PASS | see REST tables |
| Public REST | PASS | see REST tables |
| Local WS | PASS | msgs=7 |
| Public WS | PASS | msgs=8 |
| CORS | PASS | OPTIONS /status,/ws (allow-origin+methods) |

### Local REST
| Endpoint | HTTP | JSON | Snippet |
| --- | --- | --- | --- |
| health | 200 | True | {"status":"ok","timestamp_ms":1772057402109} |
| status | 200 | True | {"timestamp_ms":1772057402112,"overall_ok":false,"system":{"cpu_temp_c":38.6,"cpu_usage_percent":21.403768343499003,"loa |
| contacts | 200 | True | {"contacts":[{"id":"fpv:1","type":"FPV","source":"esp32","last_seen_ts":1772057402042,"severity":"unknown","vrx_id":1,"f |
| system | 200 | True | {"cpu_temp_c":38.6,"cpu_usage_percent":21.403768343499003,"load_1m":2.5068359375,"load_5m":2.87109375,"load_15m":1.91162 |
| power | 200 | True | {"pack_voltage_v":16.641,"current_a":-0.009,"input_vbus_v":0.0,"input_power_w":0.0,"soc_percent":98,"state":"IDLE","time |
| rf | 200 | True | {"last_event":{"reason":"no_rf_events"},"last_event_type":"RF_SCAN_OFFLINE","last_timestamp_ms":1772057400168,"scan_acti |
| video | 200 | True | {"selected":1,"status":"ok"} |
| services | 200 | True | [{"active_state":"active","name":"ndefender-backend","restart_count":0,"sub_state":"running"},{"active_state":"active"," |
| network | 200 | True | {"connected":true,"ip_v4":"192.168.1.35","ip_v6":"2401:4900:8fef:a440:69de:a6e0:f49b:2f21","ssid":"Airtel_Toybook","stat |
| audio | 200 | True | {"muted":false,"volume_percent":100,"status":"ok"} |

### Public REST
| Endpoint | HTTP | JSON | Snippet |
| --- | --- | --- | --- |
| health | 200 | True | {"status":"ok","timestamp_ms":1772057403269} |
| status | 200 | True | {"timestamp_ms":1772057404544,"overall_ok":false,"system":{"cpu_temp_c":39.7,"cpu_usage_percent":21.385291805671,"load_1 |
| contacts | 200 | True | {"contacts":[{"id":"fpv:1","type":"FPV","source":"esp32","last_seen_ts":1772057404998,"severity":"unknown","vrx_id":1,"f |
| system | 200 | True | {"cpu_temp_c":39.15,"cpu_usage_percent":21.36787378316884,"load_1m":2.4658203125,"load_5m":2.8564453125,"load_15m":1.912 |
| power | 200 | True | {"pack_voltage_v":16.642,"current_a":-0.009,"input_vbus_v":0.0,"input_power_w":0.0,"soc_percent":98,"state":"IDLE","time |
| rf | 200 | True | {"last_event":{"reason":"no_rf_events"},"last_event_type":"RF_SCAN_OFFLINE","last_timestamp_ms":1772057405168,"scan_acti |
| video | 200 | True | {"selected":1,"status":"ok"} |
| services | 200 | True | [{"active_state":"active","name":"ndefender-backend","restart_count":0,"sub_state":"running"},{"active_state":"active"," |
| network | 200 | True | {"connected":true,"ip_v4":"192.168.1.35","ip_v6":"2401:4900:8fef:a440:69de:a6e0:f49b:2f21","ssid":"Airtel_Toybook","stat |
| audio | 200 | True | {"muted":false,"volume_percent":100,"status":"ok"} |

## WebSocket
### Local WS
- connect_ok: True
- msgs_received: 7
- first_type: HELLO
- first_200: {"type":"HELLO","timestamp_ms":1772057414212,"source":"aggregator","data":{"timestamp_ms":1772057414212}}

### Public WS
- connect_ok: True
- msgs_received: 8
- first_type: HELLO
- first_200: {"type":"HELLO","timestamp_ms":1772057425252,"source":"aggregator","data":{"timestamp_ms":1772057425252}}

## CORS
- https://n.flyspark.in/api/v1/status origin=https://www.figma.com status=200 allow-origin=* allow-methods=GET, POST, OPTIONS allow-headers=Content-Type
- https://n.flyspark.in/api/v1/status origin=http://127.0.0.1 status=200 allow-origin=* allow-methods=GET, POST, OPTIONS allow-headers=Content-Type
- https://n.flyspark.in/api/v1/ws origin=https://www.figma.com status=200 allow-origin=* allow-methods=GET, POST, OPTIONS allow-headers=Content-Type
- https://n.flyspark.in/api/v1/ws origin=http://127.0.0.1 status=200 allow-origin=* allow-methods=GET, POST, OPTIONS allow-headers=Content-Type

## Command Tests
Generic endpoint probe (POST):
/command=404, /cmd=404, /control=404
| Command | HTTP | Accepted | Ack | Snippet |
| --- | --- | --- | --- | --- |
| ping | None | None | False | no generic endpoint; ping not supported |
| scan/stop | 200 | True | False | {"command":"STOP_SCAN","command_id":"7edb4758-58fb-4acb-b960-3265bb15dd04","accepted":true,"detail":null,"timestamp_ms": |
| video/select | 200 | True | False | {"command":"VIDEO_SELECT","command_id":"a56d3030-82de-476f-8183-c6e3d8202af9","accepted":true,"detail":null,"timestamp_m |

## Services
| Unit | Active | SubState | MainPID | Error |
| --- | --- | --- | --- | --- |
| ndefender-backend | active | running | 1151 | None |
| cloudflared | active | running | 1145 | None |
| ndefender-remoteid-engine | active | running | 18571 | None |
| ndefender-rfscan | active | running | 24331 | None |
| gpsd | active | running | 1205 | None |

## Subsystems
| Name | Status | Evidence |
| --- | --- | --- |
| system_metrics | PASS | cpu_usage=21.060715828190087, temp=38.05 |
| services_status | PASS | services_count=6 |
| power_ups | PASS | power fields populated |
| network | PASS | connected=True ssid=Airtel_Toybook |
| rf_pipeline | PASS | rf_last=1772057460178 rf_sensor_state=None |
| remoteid | DEGRADED | state=DEGRADED capture_active=False |
| esp32_link | FAIL | device not found: /dev/ndefender-esp32 |
| contacts_pipeline | DEGRADED | no CONTACT_* events observed in WS capture |

## Missing /status Keys
none

## Empty /status Sections
none

## RemoteID Freshness
remote_id.last_timestamp_ms=1772057460178 stale=False

## Replay/Test Contacts
blocked

## Subsystem Population Checks
power_ok=True rf_ok=True vrx_ok=True remote_id_ok=True

## Log Highlights
### ndefender-backend
(no matching error/exception/traceback/ws/403/cloudflare lines)
### cloudflared
```
Feb 26 03:26:47 ndefender-pi cloudflared[1145]: 2026-02-25T21:56:47Z INF Starting tunnel tunnelID=da648051-1eb6-42c8-abdb-552876710a96
Feb 26 03:26:47 ndefender-pi cloudflared[1145]: 2026-02-25T21:56:47Z INF Version 2026.2.0 (Checksum 03c5d58e283f521d752dc4436014eb341092edf076eb1095953ab82debe54a8e)
Feb 26 03:26:47 ndefender-pi cloudflared[1145]: 2026-02-25T21:56:47Z INF GOOS: linux, GOVersion: go1.24.13, GoArch: arm64
Feb 26 03:26:47 ndefender-pi cloudflared[1145]: 2026-02-25T21:56:47Z INF Settings: map[config:/etc/cloudflared/config.yml cred-file:/etc/cloudflared/da648051-1eb6-42c8-abdb-552876710a96.json credentials-file:/etc/cloudflared/da648051-1eb6-42c8-abdb-552876710a96.json no-autoupdate:true]
Feb 26 03:26:47 ndefender-pi cloudflared[1145]: 2026-02-25T21:56:47Z INF cloudflared will not automatically update if installed by a package manager.
Feb 26 03:26:47 ndefender-pi cloudflared[1145]: 2026-02-25T21:56:47Z INF Generated Connector ID: 23e91ff9-e5c5-4d91-a6b1-65bf0b8b9bce
Feb 26 03:26:47 ndefender-pi cloudflared[1145]: 2026-02-25T21:56:47Z INF Initial protocol quic
Feb 26 03:26:47 ndefender-pi cloudflared[1145]: 2026-02-25T21:56:47Z INF ICMP proxy will use 192.168.1.35 as source for IPv4
Feb 26 03:26:47 ndefender-pi cloudflared[1145]: 2026-02-25T21:56:47Z INF ICMP proxy will use 2401:4900:8fef:a440:69de:a6e0:f49b:2f21 in zone wlan0 as source for IPv6
Feb 26 03:26:47 ndefender-pi cloudflared[1145]: 2026-02-25T21:56:47Z INF ICMP proxy will use 192.168.1.35 as source for IPv4
Feb 26 03:26:47 ndefender-pi cloudflared[1145]: 2026-02-25T21:56:47Z INF ICMP proxy will use 2401:4900:8fef:a440:69de:a6e0:f49b:2f21 in zone wlan0 as source for IPv6
Feb 26 03:26:47 ndefender-pi cloudflared[1145]: 2026-02-25T21:56:47Z INF Starting metrics server on 127.0.0.1:20241/metrics
Feb 26 03:26:47 ndefender-pi cloudflared[1145]: 2026-02-25T21:56:47Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveP256] connIndex=0 event=0 ip=198.41.200.193
Feb 26 03:26:48 ndefender-pi cloudflared[1145]: 2026-02-25T21:56:48Z INF Registered tunnel connection connIndex=0 connection=1c843bcb-c205-4015-a8fc-aa5d4c11db55 event=0 ip=198.41.200.193 location=bom08 protocol=quic
Feb 26 03:26:48 ndefender-pi cloudflared[1145]: 2026-02-25T21:56:48Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveP256] connIndex=1 event=0 ip=198.41.192.37
Feb 26 03:26:49 ndefender-pi cloudflared[1145]: 2026-02-25T21:56:49Z INF Registered tunnel connection connIndex=1 connection=9cdeb600-d90d-4f9e-a541-f6e847e06b2f event=0 ip=198.41.192.37 location=bom06 protocol=quic
Feb 26 03:26:49 ndefender-pi cloudflared[1145]: 2026-02-25T21:56:49Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveP256] connIndex=2 event=0 ip=198.41.200.233
Feb 26 03:26:49 ndefender-pi cloudflared[1145]: 2026-02-25T21:56:49Z INF Registered tunnel connection connIndex=2 connection=9d86417f-c4f9-441a-b901-22d01dcbb63d event=0 ip=198.41.200.233 location=bom08 protocol=quic
Feb 26 03:26:50 ndefender-pi cloudflared[1145]: 2026-02-25T21:56:50Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveP256] connIndex=3 event=0 ip=198.41.192.47
Feb 26 03:26:51 ndefender-pi cloudflared[1145]: 2026-02-25T21:56:51Z INF Registered tunnel connection connIndex=3 connection=3ac71060-c11f-4354-bec0-3472deac0af6 event=0 ip=198.41.192.47 location=bom06 protocol=quic
```
### ndefender-remoteid-engine
```
Feb 26 03:35:50 ndefender-pi ndefender-remoteid[16235]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 26 03:35:55 ndefender-pi ndefender-remoteid[16401]: Traceback (most recent call last):
Feb 26 03:35:55 ndefender-pi ndefender-remoteid[16401]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
Feb 26 03:35:55 ndefender-pi ndefender-remoteid[16401]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 26 03:35:58 ndefender-pi ndefender-remoteid[16497]: Traceback (most recent call last):
Feb 26 03:35:58 ndefender-pi ndefender-remoteid[16497]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
Feb 26 03:35:58 ndefender-pi ndefender-remoteid[16497]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 26 03:36:02 ndefender-pi ndefender-remoteid[16590]: Traceback (most recent call last):
Feb 26 03:36:02 ndefender-pi ndefender-remoteid[16590]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
Feb 26 03:36:02 ndefender-pi ndefender-remoteid[16590]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 26 03:36:06 ndefender-pi ndefender-remoteid[16745]: Traceback (most recent call last):
Feb 26 03:36:06 ndefender-pi ndefender-remoteid[16745]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
Feb 26 03:36:06 ndefender-pi ndefender-remoteid[16745]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 26 03:36:09 ndefender-pi ndefender-remoteid[16839]: Traceback (most recent call last):
Feb 26 03:36:09 ndefender-pi ndefender-remoteid[16839]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
Feb 26 03:36:09 ndefender-pi ndefender-remoteid[16839]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 26 03:36:13 ndefender-pi ndefender-remoteid[16959]: Traceback (most recent call last):
Feb 26 03:36:13 ndefender-pi ndefender-remoteid[16959]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
Feb 26 03:36:13 ndefender-pi ndefender-remoteid[16959]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 26 03:36:16 ndefender-pi ndefender-remoteid[17109]: Traceback (most recent call last):
```
### ndefender-rfscan
```
Feb 26 03:39:48 ndefender-pi python3[22877]:     raise OSError(err, _strerror(err))
Feb 26 03:39:48 ndefender-pi python3[22877]: TimeoutError: [Errno 110] Connection timed out
Feb 26 03:39:48 ndefender-pi python3[22877]: During handling of the above exception, another exception occurred:
Feb 26 03:39:48 ndefender-pi python3[22877]: Traceback (most recent call last):
Feb 26 03:39:48 ndefender-pi python3[22877]:     raise Exception("No device found")
Feb 26 03:39:48 ndefender-pi python3[22877]: Exception: No device found
Feb 26 03:39:56 ndefender-pi python3[23060]: Traceback (most recent call last):
Feb 26 03:39:56 ndefender-pi python3[23060]:     raise OSError(err, _strerror(err))
Feb 26 03:39:56 ndefender-pi python3[23060]: TimeoutError: [Errno 110] Connection timed out
Feb 26 03:39:56 ndefender-pi python3[23060]: During handling of the above exception, another exception occurred:
Feb 26 03:39:56 ndefender-pi python3[23060]: Traceback (most recent call last):
Feb 26 03:39:56 ndefender-pi python3[23060]:     raise Exception("No device found")
Feb 26 03:39:56 ndefender-pi python3[23060]: Exception: No device found
Feb 26 03:40:04 ndefender-pi python3[23293]: Traceback (most recent call last):
Feb 26 03:40:04 ndefender-pi python3[23293]:     raise OSError(err, _strerror(err))
Feb 26 03:40:04 ndefender-pi python3[23293]: TimeoutError: [Errno 110] Connection timed out
Feb 26 03:40:04 ndefender-pi python3[23293]: During handling of the above exception, another exception occurred:
Feb 26 03:40:04 ndefender-pi python3[23293]: Traceback (most recent call last):
Feb 26 03:40:04 ndefender-pi python3[23293]:     raise Exception("No device found")
Feb 26 03:40:04 ndefender-pi python3[23293]: Exception: No device found
```
### gpsd
```
Feb 26 03:26:50 ndefender-pi gpsd[1205]: gpsd:ERROR: SER: Error setting port attributes: Invalid argument
```

## Conclusion
GREEN SIGNAL