# N-Defender GREEN SIGNAL Report
Generated: 2026-02-25T21:27:49Z
Hostname: ndefender-pi

## Summary
| Component | Status | Evidence |
| --- | --- | --- |
| Local REST | PASS | see REST tables |
| Public REST | PASS | see REST tables |
| Local WS | PASS | msgs=7 |
| Public WS | PASS | msgs=7 |
| CORS | PASS | OPTIONS /status,/ws (allow-origin+methods) |

### Local REST
| Endpoint | HTTP | JSON | Snippet |
| --- | --- | --- | --- |
| health | 200 | True | {"status":"ok","timestamp_ms":1772054815977} |
| status | 200 | True | {"timestamp_ms":1772054815981,"overall_ok":false,"system":{"cpu_temp_c":46.85,"cpu_usage_percent":32.04228133498624,"loa |
| contacts | 200 | True | {"contacts":[]} |
| system | 200 | True | {"cpu_temp_c":46.85,"cpu_usage_percent":32.04228133498624,"load_1m":6.71240234375,"load_5m":5.99951171875,"load_15m":3.9 |
| power | 200 | True | {"pack_voltage_v":16.709,"current_a":0.0,"input_vbus_v":0.0,"input_power_w":0.0,"soc_percent":98,"state":"IDLE","time_to |
| rf | 200 | True | {"last_event":{"center_hz":3370000000,"bandwidth_class":"narrow","family_hint":"unknown","snr_db":14.675069104690891,"pe |
| video | 200 | True | {"selected":null,"status":"unknown"} |
| services | 200 | True | [{"active_state":"active","name":"ndefender-backend","restart_count":0,"sub_state":"running"},{"active_state":"active"," |
| network | 200 | True | {"connected":true,"ip_v4":"192.168.1.35","ip_v6":"2401:4900:8fef:a440:69de:a6e0:f49b:2f21","ssid":"Airtel_Toybook","stat |
| audio | 200 | True | {"muted":false,"volume_percent":100,"status":"ok"} |

### Public REST
| Endpoint | HTTP | JSON | Snippet |
| --- | --- | --- | --- |
| health | 200 | True | {"status":"ok","timestamp_ms":1772054816850} |
| status | 200 | True | {"timestamp_ms":1772054817477,"overall_ok":false,"system":{"cpu_temp_c":46.85,"cpu_usage_percent":32.04228133498624,"loa |
| contacts | 200 | True | {"contacts":[]} |
| system | 200 | True | {"cpu_temp_c":46.85,"cpu_usage_percent":32.11071317096088,"load_1m":7.37646484375,"load_5m":6.1494140625,"load_15m":4.02 |
| power | 200 | True | {"pack_voltage_v":16.709,"current_a":0.0,"input_vbus_v":0.0,"input_power_w":0.0,"soc_percent":98,"state":"IDLE","time_to |
| rf | 200 | True | {"last_event":{"center_hz":3410000000,"bandwidth_class":"narrow","family_hint":"unknown","snr_db":13.609288099578478,"pe |
| video | 200 | True | {"selected":null,"status":"unknown"} |
| services | 200 | True | [{"active_state":"active","name":"ndefender-backend","restart_count":0,"sub_state":"running"},{"active_state":"active"," |
| network | 200 | True | {"connected":true,"ip_v4":"192.168.1.35","ip_v6":"2401:4900:8fef:a440:69de:a6e0:f49b:2f21","ssid":"Airtel_Toybook","stat |
| audio | 200 | True | {"muted":false,"volume_percent":100,"status":"ok"} |

## WebSocket
### Local WS
- connect_ok: True
- msgs_received: 7
- first_type: HELLO
- first_200: {"type":"HELLO","timestamp_ms":1772054824648,"source":"aggregator","data":{"timestamp_ms":1772054824648}}

### Public WS
- connect_ok: True
- msgs_received: 7
- first_type: HELLO
- first_200: {"type":"HELLO","timestamp_ms":1772054835595,"source":"aggregator","data":{"timestamp_ms":1772054835595}}

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
| scan/stop | 200 | False | False | {"command":"STOP_SCAN","command_id":"aa8961a7-a8d2-4d8f-9763-a95cfa683081","accepted":false,"detail":"serial not connect |
| video/select | 200 | False | False | {"command":"VIDEO_SELECT","command_id":"18f2fed6-e082-4cc9-86ab-519927b6c905","accepted":false,"detail":"serial not conn |

## Services
| Unit | Active | SubState | MainPID | Error |
| --- | --- | --- | --- | --- |
| ndefender-backend | active | running | 1053 | None |
| cloudflared | active | running | 2384 | None |
| ndefender-remoteid-engine | activating | auto-restart | 0 | None |
| ndefender-rfscan | active | running | 37903 | None |
| gpsd | active | running | 1116 | None |

## Subsystems
| Name | Status | Evidence |
| --- | --- | --- |
| system_metrics | PASS | cpu_usage=33.04594420000031, temp=47.95 |
| services_status | PASS | services_count=6 |
| power_ups | PASS | power fields populated |
| network | PASS | connected=True ssid=Airtel_Toybook |
| rf_pipeline | PASS | rf_last=1772054869393 rf_sensor_state=None |
| remoteid | DEGRADED | state=DEGRADED capture_active=False |
| esp32_link | FAIL | device not found: /dev/ndefender-esp32 |
| contacts_pipeline | DEGRADED | no CONTACT_* events observed in WS capture |

## Missing /status Keys
none

## Empty /status Sections
none

## RemoteID Freshness
remote_id.last_timestamp_ms=1772054866209 stale=False

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
Feb 26 02:56:36 ndefender-pi ndefender-remoteid[54438]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 26 02:56:40 ndefender-pi ndefender-remoteid[54602]: Traceback (most recent call last):
Feb 26 02:56:40 ndefender-pi ndefender-remoteid[54602]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
Feb 26 02:56:40 ndefender-pi ndefender-remoteid[54602]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 26 02:56:44 ndefender-pi ndefender-remoteid[54724]: Traceback (most recent call last):
Feb 26 02:56:44 ndefender-pi ndefender-remoteid[54724]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
Feb 26 02:56:44 ndefender-pi ndefender-remoteid[54724]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 26 02:56:48 ndefender-pi ndefender-remoteid[54849]: Traceback (most recent call last):
Feb 26 02:56:48 ndefender-pi ndefender-remoteid[54849]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
Feb 26 02:56:48 ndefender-pi ndefender-remoteid[54849]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 26 02:56:52 ndefender-pi ndefender-remoteid[54998]: Traceback (most recent call last):
Feb 26 02:56:52 ndefender-pi ndefender-remoteid[54998]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
Feb 26 02:56:52 ndefender-pi ndefender-remoteid[54998]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 26 02:56:56 ndefender-pi ndefender-remoteid[55100]: Traceback (most recent call last):
Feb 26 02:56:56 ndefender-pi ndefender-remoteid[55100]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
Feb 26 02:56:56 ndefender-pi ndefender-remoteid[55100]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 26 02:57:00 ndefender-pi ndefender-remoteid[55252]: Traceback (most recent call last):
Feb 26 02:57:00 ndefender-pi ndefender-remoteid[55252]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
Feb 26 02:57:00 ndefender-pi ndefender-remoteid[55252]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 26 02:57:03 ndefender-pi ndefender-remoteid[55347]: Traceback (most recent call last):
```
### ndefender-rfscan
```
Feb 26 02:57:28 ndefender-pi python3[37903]: {"t":1772054848.4403684,"detector":"peak","type":"PEAK","severity":2,"data":{"center_hz":3640000000,"peak_freq_hz":3639193733.215332,"snr_db":16.555549026207714,"peak_db":87.14504496925527,"noise_floor_db":70.58949594304755,"bandwidth_class":"narrow"}}
Feb 26 02:57:28 ndefender-pi python3[37903]: {"t":1772054848.4403684,"detector":"peak","type":"PEAK","severity":2,"data":{"center_hz":3640000000,"peak_freq_hz":3639652191.1621094,"snr_db":14.222235767587193,"peak_db":84.81173171063475,"noise_floor_db":70.58949594304755,"bandwidth_class":"narrow"}}
Feb 26 02:57:28 ndefender-pi python3[37903]: {"t":1772054848.4403684,"detector":"peak","type":"PEAK","severity":2,"data":{"center_hz":3640000000,"peak_freq_hz":3639999946.5942383,"snr_db":27.5617546197863,"peak_db":98.15125056283385,"noise_floor_db":70.58949594304755,"bandwidth_class":"narrow"}}
Feb 26 02:57:28 ndefender-pi python3[37903]: {"t":1772054848.4403684,"detector":"peak","type":"PEAK","severity":2,"data":{"center_hz":3640000000,"peak_freq_hz":3640466896.057129,"snr_db":16.67967097355256,"peak_db":87.26916691660011,"noise_floor_db":70.58949594304755,"bandwidth_class":"narrow"}}
Feb 26 02:57:28 ndefender-pi python3[37903]: {"t":1772054848.4403684,"detector":"peak","type":"PEAK","severity":2,"data":{"center_hz":3640000000,"peak_freq_hz":3640772453.3081055,"snr_db":19.1521913626716,"peak_db":89.74168730571915,"noise_floor_db":70.58949594304755,"bandwidth_class":"narrow"}}
Feb 26 02:57:29 ndefender-pi python3[37903]: {"t":1772054849.2069166,"detector":"peak","type":"PEAK","severity":2,"data":{"center_hz":3646000000,"peak_freq_hz":3646730804.4433594,"snr_db":19.468594034967182,"peak_db":90.35655681037964,"noise_floor_db":70.88796277541246,"bandwidth_class":"narrow"}}
Feb 26 02:57:29 ndefender-pi python3[37903]: {"type":"RF_CONTACT_UPDATE","ts_ms":1772054849206,"id":"rf:3646000000","data":{"center_hz":3646000000,"bandwidth_class":"narrow","family_hint":"unknown","snr_db":19.468594034967182,"peak_db":90.35655681037964}}
```
### gpsd
```
Feb 26 02:29:02 ndefender-pi gpsd[1116]: gpsd:ERROR: SER: Error setting port attributes: Invalid argument
```

## Conclusion
GREEN SIGNAL