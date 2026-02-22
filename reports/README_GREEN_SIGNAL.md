# N-Defender GREEN SIGNAL Report
Generated: 2026-02-22T15:20:31Z
Hostname: ndefender-pi

## Summary
| Component | Status | Evidence |
| --- | --- | --- |
| Local REST | PASS | see REST tables |
| Public REST | PASS | see REST tables |
| Local WS | PASS | msgs=10 |
| Public WS | PASS | msgs=10 |
| CORS | PASS | OPTIONS /status,/ws |

### Local REST
| Endpoint | HTTP | JSON | Snippet |
| --- | --- | --- | --- |
| health | 200 | True | {"status":"ok","timestamp_ms":1771773614451}  |
| status | 200 | True | {"audio":{"muted":false,"volume_percent":100},"contacts":[{"id":"rf:5758000000","last_seen_ts":1771773614338,"type":"UNK |
| contacts | 200 | True | {"contacts":[{"id":"rf:5762000000","last_seen_ts":1771773614799,"type":"UNKNOWN_RF","unknown_rf":{"bandwidth_class":"nar |
| system | 200 | True | {"cpu_temp_c":58.95,"cpu_usage_percent":65.01589558668702,"disk_total_gb":117,"disk_used_gb":69,"load_15m":6.51171875,"l |
| power | 200 | True | {"current_a":null,"input_power_w":null,"input_vbus_v":null,"pack_voltage_v":null,"per_cell_v":null,"soc_percent":null,"s |
| rf | 200 | True | {"last_event":{"id":"rf:5742000000","last_seen_ts":1771773614835,"type":"UNKNOWN_RF","unknown_rf":{"bandwidth_class":"na |
| video | 200 | True | {"selected":1,"status":"ok"}  |
| services | 200 | True | [{"active_state":"active","name":"ndefender-backend","restart_count":0,"sub_state":"running"},{"active_state":"active"," |
| network | 200 | True | {"connected":true,"ip_v4":"192.168.1.35","ip_v6":"2401:4900:8fef:a440:ae02:e0f1:7805:a92e","ssid":"Airtel_Toybook","stat |
| audio | 200 | True | {"muted":false,"status":"ok","volume_percent":100}  |

### Public REST
| Endpoint | HTTP | JSON | Snippet |
| --- | --- | --- | --- |
| health | 200 | True | {"status":"ok","timestamp_ms":1771773616232}  |
| status | 200 | True | {"audio":{"muted":false,"volume_percent":100},"contacts":[{"id":"rf:5776000000","last_seen_ts":1771773616598,"type":"UNK |
| contacts | 200 | True | {"contacts":[{"id":"rf:5788000000","last_seen_ts":1771773618201,"type":"UNKNOWN_RF","unknown_rf":{"bandwidth_class":"nar |
| system | 200 | True | {"cpu_temp_c":58.95,"cpu_usage_percent":65.01620358820186,"disk_total_gb":117,"disk_used_gb":69,"load_15m":6.51171875,"l |
| power | 200 | True | {"current_a":null,"input_power_w":null,"input_vbus_v":null,"pack_voltage_v":null,"per_cell_v":null,"soc_percent":null,"s |
| rf | 200 | True | {"last_event":{"id":"rf:5784000000","last_seen_ts":1771773620305,"type":"UNKNOWN_RF","unknown_rf":{"bandwidth_class":"na |
| video | 200 | True | {"selected":1,"status":"ok"}  |
| services | 200 | True | [{"active_state":"active","name":"ndefender-backend","restart_count":0,"sub_state":"running"},{"active_state":"active"," |
| network | 200 | True | {"connected":true,"ip_v4":"192.168.1.35","ip_v6":"2401:4900:8fef:a440:ae02:e0f1:7805:a92e","ssid":"Airtel_Toybook","stat |
| audio | 200 | True | {"muted":false,"status":"ok","volume_percent":100}  |

## WebSocket
### Local WS
- connect_ok: True
- msgs_received: 10
- first_type: CONTACT_NEW
- first_200: {"type":"CONTACT_NEW","timestamp":1771773625286,"source":"rf_sensor","data":{"id":"rf:5840000000","type":"UNKNOWN_RF","last_seen_ts":1771773624988,"unknown_rf":{"center_hz":5840000000,"snr_db":10.3617

### Public WS
- connect_ok: True
- msgs_received: 10
- first_type: CONTACT_NEW
- first_200: {"type":"CONTACT_NEW","timestamp":1771773625915,"source":"rf_sensor","data":{"id":"rf:5846000000","type":"UNKNOWN_RF","last_seen_ts":1771773625784,"unknown_rf":{"center_hz":5846000000,"snr_db":11.9564

## CORS
- https://n.flyspark.in/api/v1/status origin=https://www.figma.com status=200 allow-origin=None allow-methods=None allow-headers=None
- https://n.flyspark.in/api/v1/status origin=http://127.0.0.1 status=200 allow-origin=None allow-methods=None allow-headers=None
- https://n.flyspark.in/api/v1/ws origin=https://www.figma.com status=200 allow-origin=None allow-methods=None allow-headers=None
- https://n.flyspark.in/api/v1/ws origin=http://127.0.0.1 status=200 allow-origin=None allow-methods=None allow-headers=None

## Command Tests
Generic endpoint probe (POST):
/command=405, /cmd=405, /control=405
- error: No command endpoint found (generic: /command,/cmd,/control and direct: /vrx/tune,/scan/start,/scan/stop,/video/select)

## Services
| Unit | Active | SubState | MainPID | Error |
| --- | --- | --- | --- | --- |
| ndefender-backend | active | running | 3950898 | None |
| cloudflared | active | running | 3895612 | None |
| ndefender-remoteid-engine | active | running | 4180759 | None |
| ndefender-rfscan | active | running | 1335 | None |
| gpsd | active | running | 1489 | None |

## Subsystems
| Name | Status | Evidence |
| --- | --- | --- |
| system_metrics | PASS | cpu_usage=65.01698172949492, temp=59.5 |
| services_status | PASS | services_count=6 |
| power_ups | DEGRADED | power fields present but null |
| network | PASS | connected=True ssid=Airtel_Toybook |
| rf_pipeline | PASS | rf_last=1771773630319 rf_sensor_state=ok |
| remoteid | DEGRADED | state=DEGRADED capture_active=True |
| esp32_link | PASS | device=/dev/ndefender-esp32 |
| contacts_pipeline | PASS | contact_events=2 |

## Missing /status Keys
none

## Log Highlights
### ndefender-backend
```
Feb 22 20:50:25 ndefender-pi python[3950898]: 127.0.0.1 - - [22/Feb/2026 20:50:25] "GET /api/v1/ws HTTP/1.1" 200 -
Feb 22 20:50:26 ndefender-pi python[3950898]: 127.0.0.1 - - [22/Feb/2026 20:50:26] "GET /api/v1/ws HTTP/1.1" 200 -
Feb 22 20:50:28 ndefender-pi python[3950898]: 127.0.0.1 - - [22/Feb/2026 20:50:28] "OPTIONS /api/v1/ws HTTP/1.1" 200 -
Feb 22 20:50:29 ndefender-pi python[3950898]: 127.0.0.1 - - [22/Feb/2026 20:50:29] "OPTIONS /api/v1/ws HTTP/1.1" 200 -
```
### cloudflared
(no matching error/exception/traceback/ws/403/cloudflare lines)
### ndefender-remoteid-engine
```
Feb 22 20:49:51 ndefender-pi ndefender-remoteid[4179737]: Traceback (most recent call last):
Feb 22 20:49:52 ndefender-pi ndefender-remoteid[4179737]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
Feb 22 20:49:52 ndefender-pi ndefender-remoteid[4179737]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 22 20:49:56 ndefender-pi ndefender-remoteid[4179837]: Traceback (most recent call last):
Feb 22 20:49:56 ndefender-pi ndefender-remoteid[4179837]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
Feb 22 20:49:56 ndefender-pi ndefender-remoteid[4179837]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 22 20:50:00 ndefender-pi ndefender-remoteid[4179935]: Traceback (most recent call last):
Feb 22 20:50:00 ndefender-pi ndefender-remoteid[4179935]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
Feb 22 20:50:00 ndefender-pi ndefender-remoteid[4179935]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 22 20:50:04 ndefender-pi ndefender-remoteid[4180024]: Traceback (most recent call last):
Feb 22 20:50:04 ndefender-pi ndefender-remoteid[4180024]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
Feb 22 20:50:04 ndefender-pi ndefender-remoteid[4180024]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 22 20:50:09 ndefender-pi ndefender-remoteid[4180129]: Traceback (most recent call last):
Feb 22 20:50:09 ndefender-pi ndefender-remoteid[4180129]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
Feb 22 20:50:09 ndefender-pi ndefender-remoteid[4180129]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 22 20:50:14 ndefender-pi ndefender-remoteid[4180252]: Traceback (most recent call last):
Feb 22 20:50:14 ndefender-pi ndefender-remoteid[4180252]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
Feb 22 20:50:14 ndefender-pi ndefender-remoteid[4180252]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 22 20:50:18 ndefender-pi ndefender-remoteid[4180415]: Traceback (most recent call last):
Feb 22 20:50:18 ndefender-pi ndefender-remoteid[4180415]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
```
### ndefender-rfscan
```
Feb 22 20:50:26 ndefender-pi python3[1335]: {"t":1771773626.4261796,"detector":"peak","type":"PEAK","severity":2,"data":{"center_hz":5850000000,"peak_freq_hz":5850699928.283691,"snr_db":11.282014069862612,"peak_db":78.95409740383721,"noise_floor_db":67.6720833339746,"bandwidth_class":"narrow"}}
Feb 22 20:50:26 ndefender-pi python3[1335]: {"type":"RF_CONTACT_UPDATE","ts_ms":1771773626426,"id":"rf:5850000000","data":{"center_hz":5850000000,"bandwidth_class":"narrow","family_hint":"unknown","snr_db":11.282014069862612,"peak_db":78.95409740383721}}
Feb 22 20:50:28 ndefender-pi python3[1335]: {"t":1771773628.670342,"detector":"peak","type":"PEAK","severity":2,"data":{"center_hz":5868000000,"peak_freq_hz":5867406608.581543,"snr_db":10.654361424760722,"peak_db":78.3164744990403,"noise_floor_db":67.66211307427957,"bandwidth_class":"narrow"}}
Feb 22 20:50:28 ndefender-pi python3[1335]: {"type":"RF_CONTACT_UPDATE","ts_ms":1771773628670,"id":"rf:5868000000","data":{"center_hz":5868000000,"bandwidth_class":"narrow","family_hint":"unknown","snr_db":10.654361424760722,"peak_db":78.3164744990403}}
Feb 22 20:50:28 ndefender-pi python3[1335]: {"type":"RF_CONTACT_LOST","ts_ms":1771773628957,"id":"rf:5850000000","data":{"center_hz":5850000000,"bandwidth_class":"narrow","family_hint":"unknown","snr_db":11.282014069862612,"peak_db":78.95409740383721}}
Feb 22 20:50:29 ndefender-pi python3[1335]: {"t":1771773629.7027073,"detector":"peak","type":"PEAK","severity":2,"data":{"center_hz":5876000000,"peak_freq_hz":5876258186.340332,"snr_db":13.052611002306662,"peak_db":80.70316878279465,"noise_floor_db":67.65055778048799,"bandwidth_class":"narrow"}}
```
### gpsd
(no matching error/exception/traceback/ws/403/cloudflare lines)

## Conclusion
GREEN SIGNAL