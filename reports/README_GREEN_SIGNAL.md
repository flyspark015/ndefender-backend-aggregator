# N-Defender GREEN SIGNAL Report
Generated: 2026-02-25T21:14:33Z
Hostname: ndefender-pi

## Summary
| Component | Status | Evidence |
| --- | --- | --- |
| Local REST | PASS | see REST tables |
| Public REST | PASS | see REST tables |
| Local WS | PASS | msgs=1 |
| Public WS | PASS | msgs=1 |
| CORS | PASS | OPTIONS /status,/ws |

### Local REST
| Endpoint | HTTP | JSON | Snippet |
| --- | --- | --- | --- |
| health | 200 | True | {"status":"ok","timestamp_ms":1772054040708} |
| status | 200 | True | {"timestamp_ms":1772054040710,"overall_ok":false,"system":{"cpu_temp_c":36.95,"cpu_usage_percent":16.542836803184613,"lo |
| contacts | 200 | True | {"contacts":[]} |
| system | 200 | True | {"cpu_temp_c":36.95,"cpu_usage_percent":16.542836803184613,"load_1m":2.7060546875,"load_5m":2.1005859375,"load_15m":1.47 |
| power | 200 | True | {"pack_voltage_v":16.71,"current_a":0.0,"input_vbus_v":0.0,"input_power_w":0.0,"soc_percent":98,"state":"IDLE","time_to_ |
| rf | 200 | True | {"last_event":{"reason":"no_rf_events"},"last_event_type":"RF_SCAN_OFFLINE","last_timestamp_ms":1772054037096,"scan_acti |
| video | 200 | True | {"selected":null,"status":"unknown"} |
| services | 200 | True | [{"active_state":"active","name":"ndefender-backend","restart_count":0,"sub_state":"running"},{"active_state":"active"," |
| network | 200 | True | {"connected":true,"ip_v4":"192.168.1.35","ip_v6":"2401:4900:8fef:a440:69de:a6e0:f49b:2f21","ssid":"Airtel_Toybook","stat |
| audio | 200 | True | {"muted":false,"volume_percent":100,"status":"ok"} |

### Public REST
| Endpoint | HTTP | JSON | Snippet |
| --- | --- | --- | --- |
| health | 200 | True | {"status":"ok","timestamp_ms":1772054041322} |
| status | 200 | True | {"timestamp_ms":1772054042246,"overall_ok":false,"system":{"cpu_temp_c":36.4,"cpu_usage_percent":16.53056081020403,"load |
| contacts | 200 | True | {"contacts":[]} |
| system | 200 | True | {"cpu_temp_c":36.4,"cpu_usage_percent":16.550913559140934,"load_1m":2.6494140625,"load_5m":2.0986328125,"load_15m":1.473 |
| power | 200 | True | {"pack_voltage_v":16.71,"current_a":0.0,"input_vbus_v":0.0,"input_power_w":0.0,"soc_percent":98,"state":"IDLE","time_to_ |
| rf | 200 | True | {"last_event":{"reason":"no_rf_events"},"last_event_type":"RF_SCAN_OFFLINE","last_timestamp_ms":1772054042096,"scan_acti |
| video | 200 | True | {"selected":null,"status":"unknown"} |
| services | 200 | True | [{"active_state":"active","name":"ndefender-backend","restart_count":0,"sub_state":"running"},{"active_state":"active"," |
| network | 200 | True | {"connected":true,"ip_v4":"192.168.1.35","ip_v6":"2401:4900:8fef:a440:69de:a6e0:f49b:2f21","ssid":"Airtel_Toybook","stat |
| audio | 200 | True | {"muted":false,"volume_percent":100,"status":"ok"} |

## WebSocket
### Local WS
- connect_ok: True
- msgs_received: 1
- first_type: SYSTEM_UPDATE
- first_200: {"type":"SYSTEM_UPDATE","timestamp_ms":1772054048895,"source":"aggregator","data":{"timestamp_ms":1772054048895,"overall_ok":false,"system":{"cpu_temp_c":37.5,"cpu_usage_percent":16.555986246061867,"l

### Public WS
- connect_ok: True
- msgs_received: 1
- first_type: SYSTEM_UPDATE
- first_200: {"type":"SYSTEM_UPDATE","timestamp_ms":1772054059654,"source":"aggregator","data":{"timestamp_ms":1772054059654,"overall_ok":false,"system":{"cpu_temp_c":37.5,"cpu_usage_percent":16.55690233964585,"lo

## CORS
- https://n.flyspark.in/api/v1/status origin=https://www.figma.com status=200 allow-origin=None allow-methods=None allow-headers=None
- https://n.flyspark.in/api/v1/status origin=http://127.0.0.1 status=200 allow-origin=None allow-methods=None allow-headers=None
- https://n.flyspark.in/api/v1/ws origin=https://www.figma.com status=200 allow-origin=None allow-methods=None allow-headers=None
- https://n.flyspark.in/api/v1/ws origin=http://127.0.0.1 status=200 allow-origin=None allow-methods=None allow-headers=None

## Command Tests
Generic endpoint probe (POST):
/command=404, /cmd=404, /control=404
| Command | HTTP | Accepted | Ack | Snippet |
| --- | --- | --- | --- | --- |
| ping | None | None | False | no generic endpoint; ping not supported |
| scan/stop | 200 | False | False | {"command":"STOP_SCAN","command_id":"b720d0c1-bdfa-4830-84f8-eb5fd6b6870b","accepted":false,"detail":"serial not connect |
| video/select | 200 | False | False | {"command":"VIDEO_SELECT","command_id":"b2cf1544-a37e-42a9-af85-92ec67352ea1","accepted":false,"detail":"serial not conn |

## Services
| Unit | Active | SubState | MainPID | Error |
| --- | --- | --- | --- | --- |
| ndefender-backend | active | running | 1053 | None |
| cloudflared | active | running | 2384 | None |
| ndefender-remoteid-engine | activating | auto-restart | 0 | None |
| ndefender-rfscan | active | running | 31763 | None |
| gpsd | active | running | 1116 | None |

## Subsystems
| Name | Status | Evidence |
| --- | --- | --- |
| system_metrics | PASS | cpu_usage=16.56497753096343, temp=36.4 |
| services_status | PASS | services_count=6 |
| power_ups | PASS | power fields populated |
| network | PASS | connected=True ssid=Airtel_Toybook |
| rf_pipeline | PASS | rf_last=1772054072108 rf_sensor_state=None |
| remoteid | DEGRADED | state=DEGRADED capture_active=False |
| esp32_link | FAIL | device not found: /dev/ndefender-esp32 |
| contacts_pipeline | DEGRADED | no CONTACT_* events observed in WS capture |

## Missing /status Keys
none

## Empty /status Sections
none

## RemoteID Freshness
remote_id.last_timestamp_ms=1772054072108 stale=False

## Replay/Test Contacts
blocked

## Subsystem Population Checks
power_ok=True rf_ok=True vrx_ok=True remote_id_ok=True

## Log Highlights
### ndefender-backend
(no matching error/exception/traceback/ws/403/cloudflare lines)
### cloudflared
```
Feb 26 02:28:57 ndefender-pi cloudflared[1047]: 2026-02-25T20:58:57Z INF Starting tunnel tunnelID=da648051-1eb6-42c8-abdb-552876710a96
Feb 26 02:28:57 ndefender-pi cloudflared[1047]: 2026-02-25T20:58:57Z INF Version 2026.2.0 (Checksum 03c5d58e283f521d752dc4436014eb341092edf076eb1095953ab82debe54a8e)
Feb 26 02:28:57 ndefender-pi cloudflared[1047]: 2026-02-25T20:58:57Z INF GOOS: linux, GOVersion: go1.24.13, GoArch: arm64
Feb 26 02:28:57 ndefender-pi cloudflared[1047]: 2026-02-25T20:58:57Z INF Settings: map[config:/etc/cloudflared/config.yml cred-file:/etc/cloudflared/da648051-1eb6-42c8-abdb-552876710a96.json credentials-file:/etc/cloudflared/da648051-1eb6-42c8-abdb-552876710a96.json no-autoupdate:true]
Feb 26 02:28:57 ndefender-pi cloudflared[1047]: 2026-02-25T20:58:57Z INF cloudflared will not automatically update if installed by a package manager.
Feb 26 02:28:57 ndefender-pi cloudflared[1047]: 2026-02-25T20:58:57Z INF Generated Connector ID: 2a261028-4e54-4978-86ad-6625472e85e3
Feb 26 02:28:57 ndefender-pi cloudflared[1047]: 2026-02-25T20:58:57Z INF Initial protocol quic
Feb 26 02:29:00 ndefender-pi cloudflared[1047]: 2026-02-25T20:59:00Z INF ICMP proxy will use 192.168.1.35 as source for IPv4
Feb 26 02:29:00 ndefender-pi cloudflared[1047]: 2026-02-25T20:59:00Z INF ICMP proxy will use fe80::a0bf:f773:ab35:ec94 in zone wlan0 as source for IPv6
Feb 26 02:29:11 ndefender-pi cloudflared[1047]: 2026-02-25T20:59:11Z INF Initiating graceful shutdown due to signal terminated ...
Feb 26 02:29:12 ndefender-pi cloudflared[1047]: 2026-02-25T20:59:12Z INF ICMP proxy will use 192.168.1.35 as source for IPv4
Feb 26 02:29:12 ndefender-pi cloudflared[1047]: 2026-02-25T20:59:12Z INF ICMP proxy will use fe80::a0bf:f773:ab35:ec94 in zone wlan0 as source for IPv6
Feb 26 02:29:12 ndefender-pi cloudflared[1047]: 2026-02-25T20:59:12Z INF Starting metrics server on 127.0.0.1:20241/metrics
Feb 26 02:29:12 ndefender-pi cloudflared[1047]: 2026-02-25T20:59:12Z INF Tunnel server stopped
Feb 26 02:29:12 ndefender-pi cloudflared[1047]: 2026-02-25T20:59:12Z ERR Failed to initialize DNS local resolver error="lookup region1.v2.argotunnel.com: operation was canceled"
Feb 26 02:29:12 ndefender-pi cloudflared[1047]: 2026-02-25T20:59:12Z INF Tunnel connection curve preferences: [X25519MLKEM768 CurveP256] connIndex=0 event=0 ip=198.41.200.33
Feb 26 02:29:12 ndefender-pi cloudflared[1047]: 2026-02-25T20:59:12Z ERR icmp router terminated error="context canceled"
Feb 26 02:29:12 ndefender-pi cloudflared[1047]: 2026-02-25T20:59:12Z ERR Failed to dial a quic connection error="failed to dial to edge with quic: context canceled" connIndex=0 event=0 ip=198.41.200.33
Feb 26 02:29:12 ndefender-pi cloudflared[1047]: 2026-02-25T20:59:12Z INF Metrics server stopped
Feb 26 02:29:18 ndefender-pi cloudflared[2384]: 2026-02-25T20:59:18Z INF Starting tunnel tunnelID=da648051-1eb6-42c8-abdb-552876710a96
```
### ndefender-remoteid-engine
```
Feb 26 02:43:47 ndefender-pi ndefender-remoteid[30356]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 26 02:43:50 ndefender-pi ndefender-remoteid[30456]: Traceback (most recent call last):
Feb 26 02:43:50 ndefender-pi ndefender-remoteid[30456]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
Feb 26 02:43:50 ndefender-pi ndefender-remoteid[30456]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 26 02:43:53 ndefender-pi ndefender-remoteid[30540]: Traceback (most recent call last):
Feb 26 02:43:53 ndefender-pi ndefender-remoteid[30540]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
Feb 26 02:43:53 ndefender-pi ndefender-remoteid[30540]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 26 02:43:57 ndefender-pi ndefender-remoteid[30658]: Traceback (most recent call last):
Feb 26 02:43:57 ndefender-pi ndefender-remoteid[30658]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
Feb 26 02:43:57 ndefender-pi ndefender-remoteid[30658]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 26 02:44:00 ndefender-pi ndefender-remoteid[30760]: Traceback (most recent call last):
Feb 26 02:44:00 ndefender-pi ndefender-remoteid[30760]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
Feb 26 02:44:00 ndefender-pi ndefender-remoteid[30760]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 26 02:44:04 ndefender-pi ndefender-remoteid[30912]: Traceback (most recent call last):
Feb 26 02:44:04 ndefender-pi ndefender-remoteid[30912]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
Feb 26 02:44:04 ndefender-pi ndefender-remoteid[30912]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 26 02:44:07 ndefender-pi ndefender-remoteid[30997]: Traceback (most recent call last):
Feb 26 02:44:07 ndefender-pi ndefender-remoteid[30997]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
Feb 26 02:44:07 ndefender-pi ndefender-remoteid[30997]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 26 02:44:10 ndefender-pi ndefender-remoteid[31089]: Traceback (most recent call last):
```
### ndefender-rfscan
```
Feb 26 02:43:41 ndefender-pi python3[30018]:     raise OSError(err, _strerror(err))
Feb 26 02:43:41 ndefender-pi python3[30018]: TimeoutError: [Errno 110] Connection timed out
Feb 26 02:43:41 ndefender-pi python3[30018]: During handling of the above exception, another exception occurred:
Feb 26 02:43:41 ndefender-pi python3[30018]: Traceback (most recent call last):
Feb 26 02:43:41 ndefender-pi python3[30018]:     raise Exception("No device found")
Feb 26 02:43:41 ndefender-pi python3[30018]: Exception: No device found
Feb 26 02:43:50 ndefender-pi python3[30348]: Traceback (most recent call last):
Feb 26 02:43:50 ndefender-pi python3[30348]:     raise OSError(err, _strerror(err))
Feb 26 02:43:50 ndefender-pi python3[30348]: TimeoutError: [Errno 110] Connection timed out
Feb 26 02:43:50 ndefender-pi python3[30348]: During handling of the above exception, another exception occurred:
Feb 26 02:43:50 ndefender-pi python3[30348]: Traceback (most recent call last):
Feb 26 02:43:50 ndefender-pi python3[30348]:     raise Exception("No device found")
Feb 26 02:43:50 ndefender-pi python3[30348]: Exception: No device found
Feb 26 02:43:58 ndefender-pi python3[30552]: Traceback (most recent call last):
Feb 26 02:43:58 ndefender-pi python3[30552]:     raise OSError(err, _strerror(err))
Feb 26 02:43:58 ndefender-pi python3[30552]: TimeoutError: [Errno 110] Connection timed out
Feb 26 02:43:58 ndefender-pi python3[30552]: During handling of the above exception, another exception occurred:
Feb 26 02:43:58 ndefender-pi python3[30552]: Traceback (most recent call last):
Feb 26 02:43:58 ndefender-pi python3[30552]:     raise Exception("No device found")
Feb 26 02:43:58 ndefender-pi python3[30552]: Exception: No device found
```
### gpsd
```
Feb 26 02:29:02 ndefender-pi gpsd[1116]: gpsd:ERROR: SER: Error setting port attributes: Invalid argument
```

## Conclusion
GREEN SIGNAL