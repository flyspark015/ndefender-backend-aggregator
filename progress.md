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
