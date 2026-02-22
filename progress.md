# Progress Log ✅

Why this exists: This log provides a traceable record of each delivery step, verification, and any follow-up required for production readiness.

## Current Step
- Step 1: Roadmap + Repo Skeleton — 🟢 complete
- Step 2: Configuration Layer — 🟢 complete
- Step 3: Application Foundation (Auth + CI) — 🟢 complete
- Step 4: State Core + WebSocket Enhancements — 🟢 complete
- Step 5: Internal Event Bus Scaffold — 🟢 complete
- Step 6: Ingestion Contracts (No Integrations) — 🟢 complete
- Step 7: Command Routing Contracts (No Integrations) — 🟢 complete
- Step 8: Integration Stubs (No Wiring) — 🟢 complete
- Step 9: Runtime Orchestration (No Integrations) — 🟢 complete
- Step 10: System Controller Integration — 🟢 complete
- Step 11: ESP32 Serial Integration — 🟢 complete
- Step 12: AntSDR JSONL Integration — 🟢 complete
- Step 13: RemoteID JSONL Integration — 🟢 complete
- Step 14: Contact Unification + Status Aggregation — 🟢 complete
- Step 15: System Controller Command Routing — 🟢 complete
- Step 16: Final Hardening Tools + Ops Checklist — 🟢 complete

## 🔒 Release Lock — v0.1.0
- Final verification evidence:
  - `ruff check .` -> `All checks passed!`
  - `pytest` -> `25 passed in 2.31s`
- Tag confirmation:
  - `v0.1.0` -> `9496359 Finalize roadmap and release validation`
- CI confirmation: Passing
- Statement: Runtime logic frozen for v0.1.0

## Public API Exposure (2026-02-22)
- Step A: Cloudflared install on Pi — ✅
- Step B: Cloudflared auth + tunnel create — ✅
- Step C: CORS policy + WS origin enforcement — ✅
- Step D: Public HTTPS/WSS verification + evidence capture — ✅

### Evidence
1) `curl -I https://n.flyspark.in/api/v1/health`
```
HTTP/2 200
content-type: application/json
access-control-allow-headers: Content-Type,X-API-Key,X-Role
access-control-allow-methods: GET,POST,OPTIONS
```

2) `curl https://n.flyspark.in/api/v1/status`
```
{"contacts":[{"id":"rf:3586000000","last_seen_ts":1771757937112,"type":"UNKNOWN_RF"}
```

3) CORS preflight (OPTIONS)
```
HTTP/2 200
access-control-allow-origin: https://www.figma.com
access-control-allow-methods: GET,POST,OPTIONS
access-control-allow-headers: Content-Type,X-API-Key,X-Role
```

4) WSS test
```
{"type":"CONTACT_NEW","timestamp":1771757947009,"source":"rf_sensor",...}
CONTACT_NEW
```

## Public Test Mode (2026-02-22)
- [x] PUBLIC_TEST_MODE toggle added
- [x] CORS open verified
- [x] WS open verified
- [x] curl tests recorded (outputs)
- [x] revert steps recorded

### Evidence
1) `curl -i https://n.flyspark.in/api/v1/health`
```
HTTP/2 200
access-control-allow-origin: *
access-control-allow-methods: GET,POST,OPTIONS
access-control-allow-headers: Content-Type,X-API-Key,X-Role
```

2) `curl -i -X OPTIONS https://n.flyspark.in/api/v1/status \
  -H "Origin: https://www.figma.com" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Content-Type"`
```
HTTP/2 200
access-control-allow-origin: *
access-control-allow-methods: GET,POST,OPTIONS
access-control-allow-headers: Content-Type,X-API-Key,X-Role
```

3) `python3 tools/ws_public_test.py`
```
connected
received=1, first_type=CONTACT_NEW
```

Revert steps recorded in `docs/PUBLIC_TEST_MODE.md`.

## Diagnostics Runner (2026-02-22)
- [x] Runner skeleton + REST probes + report generation
- [x] Local run completed

Evidence:
- report_md: `reports/diagnostics_20260222_115655.md`
- report_json: `reports/diagnostics_20260222_115655.json`
- summary snippet:
```
health PASS 200
status DEGRADED 200
contacts FAIL 404
```

## Inventory Snapshot (2026-02-22)
Evidence:
1) Listener map (ports 443/8000/9109)
```
LISTEN 0 4096 100.99.78.121:443 0.0.0.0:* users:("tailscaled",pid=913,fd=24))
LISTEN 0  128 0.0.0.0:8000       0.0.0.0:* users:("python",pid=3900428,fd=12))
LISTEN 0 2048 0.0.0.0:9109       0.0.0.0:* users:("uvicorn",pid=66862,fd=8))
```

2) Backend process + service
```
/opt/ndefender/backend/venv/bin/python -u /opt/ndefender/backend/app.py
ndefender-backend.service active (running)
```

3) API reality (local)
```
GET /api/v1/health -> 200
GET /api/v1/status -> JSON (contacts...)
```

Report file:
- `reports/inventory_20260222_120413.md`

## Contract Alignment Plan (2026-02-22)
Decision: Option A (implement missing REST endpoints in backend on port 8000).

Evidence:
1) Contract-required Aggregator endpoints (from `ndefender-api-contracts/docs/OPENAPI.yaml`)
```
/health
/status
/contacts
/system
/power
/rf
/video
/services
/network
/audio
/ws
```

2) Running backend routes (from `/opt/ndefender/backend/app.py`)
```
/api/v1/health
/api/v1/status
/api/v1/ws
... (no /api/v1/contacts|system|power|rf|video|services|network|audio base routes)
```

Plan:
- Implement missing endpoints in the backend that is actually running on 8000 (currently `/opt/ndefender/backend/app.py`).
- Ensure JSON contract alignment (gps.latitude/longitude, freq_hz, timestamp_ms, etc.) and ms timestamps.
- If a subsystem is unavailable, return valid JSON with nulls + status=degraded.
- Ensure `/api/v1/status` includes cpu, ram, disk, ups, services, rf, network, audio, video (even if degraded).

## Step 3 Backend Fix (2026-02-22)
Implemented missing v1 endpoints in the live backend (`/opt/ndefender/backend/app.py`) and restarted `ndefender-backend`.

Evidence (local):
1) `GET /api/v1/system`
```
{"cpu_temp_c":62.25,"cpu_usage_percent":64.24754557338834,"disk_total_gb":117,"disk_used_gb":69,"load_15m":6.83984375,"load_1m":6.23876953125,"load_5m":6.650390625,"ram_total_mb":16215,"ram_used_mb":7822,"status":"ok","throttled_flags":0,"uptime_s":346001}
```

2) `GET /api/v1/network`
```
{"connected":true,"ip_v4":"192.168.1.35","ip_v6":"2401:4900:8fef:a440:ae02:e0f1:7805:a92e","ssid":"Airtel_Toybook","status":"ok"}
```
