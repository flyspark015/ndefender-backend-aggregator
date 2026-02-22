# N-Defender GREEN SIGNAL Report
Generated: 2026-02-22T14:38:56Z
Hostname: ndefender-pi

## Summary
| Component | Status | Evidence |
| --- | --- | --- |
| Local REST | PASS | see REST tables |
| Public REST | FAIL | see REST tables |
| Local WS | PASS | msgs=10 |
| Public WS | PASS | msgs=10 |
| CORS | FAIL | OPTIONS /status,/ws |

### Local REST
| Endpoint | HTTP | JSON | Snippet |
| --- | --- | --- | --- |
| health | 200 | True | {"status":"ok","timestamp_ms":1771771124530}  |
| status | 200 | True | {"audio":{"muted":false,"volume_percent":100},"contacts":[{"id":"rf:1350000000","last_seen_ts":1771771124353,"type":"UNK |
| contacts | 200 | True | {"contacts":[{"id":"rf:1354000000","last_seen_ts":1771771124947,"type":"UNKNOWN_RF","unknown_rf":{"bandwidth_class":"nar |
| system | 200 | True | {"cpu_temp_c":60.05,"cpu_usage_percent":64.84654263354707,"disk_total_gb":117,"disk_used_gb":69,"load_15m":6.29150390625 |
| power | 200 | True | {"current_a":null,"input_power_w":null,"input_vbus_v":null,"pack_voltage_v":null,"per_cell_v":null,"soc_percent":null,"s |
| rf | 200 | True | {"last_event":{"id":"rf:1356000000","last_seen_ts":1771771125253,"type":"UNKNOWN_RF","unknown_rf":{"bandwidth_class":"na |
| video | 200 | True | {"selected":1,"status":"ok"}  |
| services | 200 | True | [{"active_state":"active","name":"ndefender-backend","restart_count":0,"sub_state":"running"},{"active_state":"active"," |
| network | 200 | True | {"connected":true,"ip_v4":"192.168.1.35","ip_v6":"2401:4900:8fef:a440:ae02:e0f1:7805:a92e","ssid":"Airtel_Toybook","stat |
| audio | 200 | True | {"muted":false,"status":"ok","volume_percent":100}  |

### Public REST
| Endpoint | HTTP | JSON | Snippet |
| --- | --- | --- | --- |
| health | 403 | False | error code: 1010 |
| status | 403 | False | error code: 1010 |
| contacts | 403 | False | error code: 1010 |
| system | 403 | False | error code: 1010 |
| power | 403 | False | error code: 1010 |
| rf | 403 | False | error code: 1010 |
| video | 403 | False | error code: 1010 |
| services | 403 | False | error code: 1010 |
| network | 403 | False | error code: 1010 |
| audio | 403 | False | error code: 1010 |

## WebSocket
### Local WS
- connect_ok: True
- msgs_received: 10
- first_type: CONTACT_NEW
- first_200: {"type":"CONTACT_NEW","timestamp":1771771132464,"source":"rf_sensor","data":{"id":"rf:3144000000","type":"UNKNOWN_RF","last_seen_ts":1771771132349,"unknown_rf":{"center_hz":3144000000,"snr_db":10.8246

### Public WS
- connect_ok: True
- msgs_received: 10
- first_type: CONTACT_NEW
- first_200: {"type":"CONTACT_NEW","timestamp":1771771133140,"source":"rf_sensor","data":{"id":"rf:3148000000","type":"UNKNOWN_RF","last_seen_ts":1771771132871,"unknown_rf":{"center_hz":3148000000,"snr_db":11.8190

## CORS
- https://n.flyspark.in/api/v1/status origin=https://www.figma.com status=403 allow-origin=None allow-methods=None allow-headers=None
- https://n.flyspark.in/api/v1/status origin=http://127.0.0.1 status=403 allow-origin=None allow-methods=None allow-headers=None
- https://n.flyspark.in/api/v1/ws origin=https://www.figma.com status=403 allow-origin=None allow-methods=None allow-headers=None
- https://n.flyspark.in/api/v1/ws origin=http://127.0.0.1 status=403 allow-origin=None allow-methods=None allow-headers=None

## Command Tests
Generic endpoint probe (POST):
/command=405, /cmd=405, /control=405
- error: No command endpoint found (generic: /command,/cmd,/control and direct: /vrx/tune,/scan/start,/scan/stop,/video/select)

## Services
| Unit | Active | SubState | MainPID | Error |
| --- | --- | --- | --- | --- |
| ndefender-backend | active | running | 3950898 | None |
| cloudflared | active | running | 3895612 | None |
| ndefender-remoteid-engine | activating | auto-restart | 0 | None |
| ndefender-rfscan | active | running | 1335 | None |
| gpsd | active | running | 1489 | None |

## Subsystems
| Name | Status | Evidence |
| --- | --- | --- |
| system_metrics | PASS | cpu_usage=64.84731418583381, temp=58.95 |
| services_status | PASS | services_count=6 |
| power_ups | DEGRADED | power fields present but null |
| network | PASS | connected=True ssid=Airtel_Toybook |
| rf_pipeline | PASS | rf_last=1771771136057 rf_sensor_state=ok |
| remoteid | DEGRADED | state=DEGRADED capture_active=True |
| esp32_link | PASS | device=/dev/ndefender-esp32 |
| contacts_pipeline | PASS | contact_events=2 |

## Missing /status Keys
none

## Log Highlights
### ndefender-backend
```
Feb 22 20:06:25 ndefender-pi python[3950898]: 127.0.0.1 - - [22/Feb/2026 20:06:25] "GET /api/v1/ws HTTP/1.1" 200 -
Feb 22 20:06:27 ndefender-pi python[3950898]: 127.0.0.1 - - [22/Feb/2026 20:06:27] "GET /api/v1/ws HTTP/1.1" 200 -
Feb 22 20:08:07 ndefender-pi python[3950898]: PLAY_SOUND req_id=u_mlxurcws_14b_6gm0w sound_name=drone_detected_alarm exit_code=-15 timed_out=False ok=False
Feb 22 20:08:52 ndefender-pi python[3950898]: 127.0.0.1 - - [22/Feb/2026 20:08:52] "GET /api/v1/ws HTTP/1.1" 200 -
Feb 22 20:08:53 ndefender-pi python[3950898]: 127.0.0.1 - - [22/Feb/2026 20:08:53] "GET /api/v1/ws HTTP/1.1" 200 -
```
### cloudflared
(no matching error/exception/traceback/ws/403/cloudflare lines)
### ndefender-remoteid-engine
```
Feb 22 20:08:19 ndefender-pi ndefender-remoteid[4128636]: Traceback (most recent call last):
Feb 22 20:08:19 ndefender-pi ndefender-remoteid[4128636]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
Feb 22 20:08:19 ndefender-pi ndefender-remoteid[4128636]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 22 20:08:23 ndefender-pi ndefender-remoteid[4128763]: Traceback (most recent call last):
Feb 22 20:08:23 ndefender-pi ndefender-remoteid[4128763]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
Feb 22 20:08:23 ndefender-pi ndefender-remoteid[4128763]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 22 20:08:28 ndefender-pi ndefender-remoteid[4128849]: Traceback (most recent call last):
Feb 22 20:08:28 ndefender-pi ndefender-remoteid[4128849]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
Feb 22 20:08:28 ndefender-pi ndefender-remoteid[4128849]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 22 20:08:32 ndefender-pi ndefender-remoteid[4128966]: Traceback (most recent call last):
Feb 22 20:08:32 ndefender-pi ndefender-remoteid[4128966]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
Feb 22 20:08:32 ndefender-pi ndefender-remoteid[4128966]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 22 20:08:37 ndefender-pi ndefender-remoteid[4129081]: Traceback (most recent call last):
Feb 22 20:08:37 ndefender-pi ndefender-remoteid[4129081]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
Feb 22 20:08:37 ndefender-pi ndefender-remoteid[4129081]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 22 20:08:41 ndefender-pi ndefender-remoteid[4129179]: Traceback (most recent call last):
Feb 22 20:08:41 ndefender-pi ndefender-remoteid[4129179]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
Feb 22 20:08:41 ndefender-pi ndefender-remoteid[4129179]: RuntimeError: tshark exited with 1: Capturing on 'mon0'
Feb 22 20:08:46 ndefender-pi ndefender-remoteid[4129296]: Traceback (most recent call last):
Feb 22 20:08:46 ndefender-pi ndefender-remoteid[4129296]:     raise RuntimeError(f"tshark exited with {returncode}: {stderr_output}")
```
### ndefender-rfscan
```
Feb 22 20:08:51 ndefender-pi python3[1335]: {"t":1771771131.569671,"detector":"peak","type":"PEAK","severity":2,"data":{"center_hz":3138000000,"peak_freq_hz":3137740348.815918,"snr_db":12.179810333043037,"peak_db":80.84393045520679,"noise_floor_db":68.66412012216375,"bandwidth_class":"narrow"}}
Feb 22 20:08:53 ndefender-pi python3[1335]: {"t":1771771133.1541667,"detector":"peak","type":"PEAK","severity":2,"data":{"center_hz":3150000000,"peak_freq_hz":3149179786.682129,"snr_db":10.645509142240343,"peak_db":79.23322834107188,"noise_floor_db":68.58771919883154,"bandwidth_class":"narrow"}}
Feb 22 20:08:53 ndefender-pi python3[1335]: {"type":"RF_CONTACT_NEW","ts_ms":1771771133154,"id":"rf:3150000000","data":{"center_hz":3150000000,"bandwidth_class":"narrow","family_hint":"unknown","snr_db":10.645509142240343,"peak_db":79.23322834107188}}
Feb 22 20:08:54 ndefender-pi python3[1335]: {"t":1771771134.2121303,"detector":"peak","type":"PEAK","severity":2,"data":{"center_hz":3158000000,"peak_freq_hz":3158359107.9711914,"snr_db":12.487470140316859,"peak_db":81.0884022541203,"noise_floor_db":68.60093211380344,"bandwidth_class":"narrow"}}
Feb 22 20:08:54 ndefender-pi python3[1335]: {"type":"RF_CONTACT_UPDATE","ts_ms":1771771134212,"id":"rf:3158000000","data":{"center_hz":3158000000,"bandwidth_class":"narrow","family_hint":"unknown","snr_db":12.487470140316859,"peak_db":81.0884022541203}}
Feb 22 20:08:54 ndefender-pi python3[1335]: {"t":1771771134.2121303,"detector":"peak","type":"PEAK","severity":2,"data":{"center_hz":3158000000,"peak_freq_hz":3158683433.532715,"snr_db":11.065074271600096,"peak_db":79.66600638540353,"noise_floor_db":68.60093211380344,"bandwidth_class":"narrow"}}
Feb 22 20:08:54 ndefender-pi python3[1335]: {"type":"RF_CONTACT_UPDATE","ts_ms":1771771134212,"id":"rf:3158000000","data":{"center_hz":3158000000,"bandwidth_class":"narrow","family_hint":"unknown","snr_db":11.065074271600096,"peak_db":79.66600638540353}}
```
### gpsd
(no matching error/exception/traceback/ws/403/cloudflare lines)

## Conclusion
RED SIGNAL

## Root Cause If Not Green
- Public REST failing (likely Cloudflare 403 for non-browser clients)
- CORS preflight failing

## Fix Plan
1. Verify Cloudflare WAF Skip rule for /api/v1/* (Managed Rules, BIC, Bot Fight).
2. Re-run diagnostics after rule is active.