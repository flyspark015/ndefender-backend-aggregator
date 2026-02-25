# N-Defender GREEN SIGNAL Report
Generated: 2026-02-25T21:38:24Z
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
| health | 200 | True | {"status":"ok","timestamp_ms":1772055450635} |
| status | 200 | True | {"timestamp_ms":1772055450639,"overall_ok":false,"system":{"cpu_temp_c":46.85,"cpu_usage_percent":40.96278997279734,"loa |
| contacts | 200 | True | {"contacts":[]} |
| system | 200 | True | {"cpu_temp_c":46.85,"cpu_usage_percent":40.96278997279734,"load_1m":6.64208984375,"load_5m":6.17236328125,"load_15m":5.0 |
| power | 200 | True | {"pack_voltage_v":16.709,"current_a":0.0,"input_vbus_v":0.0,"input_power_w":0.0,"soc_percent":98,"state":"IDLE","time_to |
| rf | 200 | True | {"last_event":{"center_hz":3366000000,"bandwidth_class":"narrow","family_hint":"unknown","snr_db":32.96927092178615,"pea |
| video | 200 | True | {"selected":null,"status":"unknown"} |
| services | 200 | True | [{"active_state":"active","name":"ndefender-backend","restart_count":0,"sub_state":"running"},{"active_state":"active"," |
| network | 200 | True | {"connected":true,"ip_v4":"192.168.1.35","ip_v6":"2401:4900:8fef:a440:69de:a6e0:f49b:2f21","ssid":"Airtel_Toybook","stat |
| audio | 200 | True | {"muted":false,"volume_percent":100,"status":"ok"} |

### Public REST
| Endpoint | HTTP | JSON | Snippet |
| --- | --- | --- | --- |
| health | 200 | True | {"status":"ok","timestamp_ms":1772055451417} |
| status | 200 | True | {"timestamp_ms":1772055452328,"overall_ok":false,"system":{"cpu_temp_c":46.85,"cpu_usage_percent":40.96278997279734,"loa |
| contacts | 200 | True | {"contacts":[]} |
| system | 200 | True | {"cpu_temp_c":47.95,"cpu_usage_percent":40.99649483660655,"load_1m":6.35009765625,"load_5m":6.11962890625,"load_15m":5.0 |
| power | 200 | True | {"pack_voltage_v":16.709,"current_a":0.0,"input_vbus_v":0.0,"input_power_w":0.0,"soc_percent":98,"state":"IDLE","time_to |
| rf | 200 | True | {"last_event":{"center_hz":3406000000,"bandwidth_class":"narrow","family_hint":"unknown","snr_db":15.18393927204508,"pea |
| video | 200 | True | {"selected":null,"status":"unknown"} |
| services | 200 | True | [{"active_state":"active","name":"ndefender-backend","restart_count":0,"sub_state":"running"},{"active_state":"active"," |
| network | 200 | True | {"connected":true,"ip_v4":"192.168.1.35","ip_v6":"2401:4900:8fef:a440:69de:a6e0:f49b:2f21","ssid":"Airtel_Toybook","stat |
| audio | 200 | True | {"muted":false,"volume_percent":100,"status":"ok"} |

## WebSocket
### Local WS
- connect_ok: True
- msgs_received: 7
- first_type: HELLO
- first_200: {"type":"HELLO","timestamp_ms":1772055459435,"source":"aggregator","data":{"timestamp_ms":1772055459435}}

### Public WS
- connect_ok: True
- msgs_received: 7
- first_type: HELLO
- first_200: {"type":"HELLO","timestamp_ms":1772055470117,"source":"aggregator","data":{"timestamp_ms":1772055470117}}

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
| scan/stop | 200 | False | False | {"command":"STOP_SCAN","command_id":"0b743efa-a68a-4e40-a8da-1b025b2ec891","accepted":false,"detail":"serial not connect |
| video/select | 200 | False | False | {"command":"VIDEO_SELECT","command_id":"c4cf6137-482e-45e0-a316-f2cf88d7137e","accepted":false,"detail":"serial not conn |

## Services
| Unit | Active | SubState | MainPID | Error |
| --- | --- | --- | --- | --- |
| ndefender-backend | active | running | 1053 | None |
| cloudflared | active | running | 2384 | None |
| ndefender-remoteid-engine | active | running | 75502 | None |
| ndefender-rfscan | active | running | 37903 | None |
| gpsd | active | running | 1116 | None |

## Subsystems
| Name | Status | Evidence |
| --- | --- | --- |
| system_metrics | PASS | cpu_usage=41.54593054886564, temp=46.85 |
| services_status | PASS | services_count=6 |
| power_ups | PASS | power fields populated |
| network | PASS | connected=True ssid=Airtel_Toybook |
| rf_pipeline | PASS | rf_last=1772055504033 rf_sensor_state=None |
| remoteid | DEGRADED | state=DEGRADED capture_active=False |
| esp32_link | FAIL | device not found: /dev/ndefender-esp32 |
| contacts_pipeline | DEGRADED | no CONTACT_* events observed in WS capture |

## Missing /status Keys
none

## Empty /status Sections
none

## RemoteID Freshness
remote_id.last_timestamp_ms=1772055501420 stale=False

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
Feb 26 03:07:09 ndefender-pi ndefender-remoteid[73726]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 26 03:07:13 ndefender-pi ndefender-remoteid[73839]: Traceback (most recent call last):
Feb 26 03:07:13 ndefender-pi ndefender-remoteid[73839]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
Feb 26 03:07:13 ndefender-pi ndefender-remoteid[73839]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 26 03:07:17 ndefender-pi ndefender-remoteid[73978]: Traceback (most recent call last):
Feb 26 03:07:17 ndefender-pi ndefender-remoteid[73978]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
Feb 26 03:07:17 ndefender-pi ndefender-remoteid[73978]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 26 03:07:21 ndefender-pi ndefender-remoteid[74103]: Traceback (most recent call last):
Feb 26 03:07:21 ndefender-pi ndefender-remoteid[74103]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
Feb 26 03:07:21 ndefender-pi ndefender-remoteid[74103]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 26 03:07:25 ndefender-pi ndefender-remoteid[74244]: Traceback (most recent call last):
Feb 26 03:07:25 ndefender-pi ndefender-remoteid[74244]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
Feb 26 03:07:25 ndefender-pi ndefender-remoteid[74244]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 26 03:07:29 ndefender-pi ndefender-remoteid[74373]: Traceback (most recent call last):
Feb 26 03:07:29 ndefender-pi ndefender-remoteid[74373]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
Feb 26 03:07:29 ndefender-pi ndefender-remoteid[74373]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 26 03:07:32 ndefender-pi ndefender-remoteid[74515]: Traceback (most recent call last):
Feb 26 03:07:32 ndefender-pi ndefender-remoteid[74515]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
Feb 26 03:07:32 ndefender-pi ndefender-remoteid[74515]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 26 03:07:37 ndefender-pi ndefender-remoteid[74620]: Traceback (most recent call last):
```
### ndefender-rfscan
```
Feb 26 03:08:00 ndefender-pi python3[37903]: {"t":1772055480.1329293,"detector":"peak","type":"PEAK","severity":2,"data":{"center_hz":3612000000,"peak_freq_hz":3611235549.926758,"snr_db":22.263290946808155,"peak_db":92.8751312507366,"noise_floor_db":70.61184030392845,"bandwidth_class":"narrow"}}
Feb 26 03:08:00 ndefender-pi python3[37903]: {"t":1772055480.1329293,"detector":"peak","type":"PEAK","severity":2,"data":{"center_hz":3612000000,"peak_freq_hz":3611744812.0117188,"snr_db":18.64120091809548,"peak_db":89.25304122202392,"noise_floor_db":70.61184030392845,"bandwidth_class":"narrow"}}
Feb 26 03:08:00 ndefender-pi python3[37903]: {"t":1772055480.1329293,"detector":"peak","type":"PEAK","severity":2,"data":{"center_hz":3612000000,"peak_freq_hz":3611999969.482422,"snr_db":26.57950219801735,"peak_db":97.1913425019458,"noise_floor_db":70.61184030392845,"bandwidth_class":"narrow"}}
Feb 26 03:08:00 ndefender-pi python3[37903]: {"t":1772055480.1329293,"detector":"peak","type":"PEAK","severity":2,"data":{"center_hz":3612000000,"peak_freq_hz":3612254081.726074,"snr_db":20.134904990967314,"peak_db":90.74674529489576,"noise_floor_db":70.61184030392845,"bandwidth_class":"narrow"}}
Feb 26 03:08:00 ndefender-pi python3[37903]: {"t":1772055480.1329293,"detector":"peak","type":"PEAK","severity":2,"data":{"center_hz":3612000000,"peak_freq_hz":3612508712.7685547,"snr_db":16.706585374080532,"peak_db":87.31842567800898,"noise_floor_db":70.61184030392845,"bandwidth_class":"narrow"}}
Feb 26 03:08:00 ndefender-pi python3[37903]: {"t":1772055480.1329293,"detector":"peak","type":"PEAK","severity":2,"data":{"center_hz":3612000000,"peak_freq_hz":3612763343.811035,"snr_db":21.551505031722584,"peak_db":92.16334533565103,"noise_floor_db":70.61184030392845,"bandwidth_class":"narrow"}}
Feb 26 03:08:01 ndefender-pi python3[37903]: {"t":1772055481.1738384,"detector":"peak","type":"PEAK","severity":2,"data":{"center_hz":3620000000,"peak_freq_hz":3619180046.081543,"snr_db":44.24311538856526,"peak_db":115.02648809114032,"noise_floor_db":70.78337270257506,"bandwidth_class":"narrow"}}
Feb 26 03:08:01 ndefender-pi python3[37903]: {"type":"RF_CONTACT_NEW","ts_ms":1772055481173,"id":"rf:3620000000","data":{"center_hz":3620000000,"bandwidth_class":"narrow","family_hint":"unknown","snr_db":44.24311538856526,"peak_db":115.02648809114032}}
Feb 26 03:08:02 ndefender-pi python3[37903]: {"t":1772055482.2279408,"detector":"peak","type":"PEAK","severity":2,"data":{"center_hz":3628000000,"peak_freq_hz":3627999977.1118164,"snr_db":26.4334178576445,"peak_db":96.88847969403788,"noise_floor_db":70.45506183639338,"bandwidth_class":"narrow"}}
Feb 26 03:08:02 ndefender-pi python3[37903]: {"t":1772055482.7398894,"detector":"peak","type":"PEAK","severity":2,"data":{"center_hz":3632000000,"peak_freq_hz":3631147712.7075195,"snr_db":18.82214978413981,"peak_db":89.45965418740508,"noise_floor_db":70.63750440326527,"bandwidth_class":"narrow"}}
Feb 26 03:08:02 ndefender-pi python3[37903]: {"t":1772055482.7398894,"detector":"peak","type":"PEAK","severity":2,"data":{"center_hz":3632000000,"peak_freq_hz":3631555122.3754883,"snr_db":16.39533803429704,"peak_db":87.03284243756231,"noise_floor_db":70.63750440326527,"bandwidth_class":"narrow"}}
Feb 26 03:08:02 ndefender-pi python3[37903]: {"t":1772055482.7398894,"detector":"peak","type":"PEAK","severity":2,"data":{"center_hz":3632000000,"peak_freq_hz":3632000045.776367,"snr_db":27.86584046211901,"peak_db":98.50334486538428,"noise_floor_db":70.63750440326527,"bandwidth_class":"narrow"}}
Feb 26 03:08:02 ndefender-pi python3[37903]: {"t":1772055482.7398894,"detector":"peak","type":"PEAK","severity":2,"data":{"center_hz":3632000000,"peak_freq_hz":3632471794.128418,"snr_db":16.10640021169678,"peak_db":86.74390461496205,"noise_floor_db":70.63750440326527,"bandwidth_class":"narrow"}}
Feb 26 03:08:02 ndefender-pi python3[37903]: {"t":1772055482.7398894,"detector":"peak","type":"PEAK","severity":2,"data":{"center_hz":3632000000,"peak_freq_hz":3632726425.1708984,"snr_db":17.529468485374352,"peak_db":88.16697288863962,"noise_floor_db":70.63750440326527,"bandwidth_class":"narrow"}}
```
### gpsd
```
Feb 26 02:29:02 ndefender-pi gpsd[1116]: gpsd:ERROR: SER: Error setting port attributes: Invalid argument
```

## Conclusion
GREEN SIGNAL