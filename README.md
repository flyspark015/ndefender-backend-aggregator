# 🛰 N-Defender Backend Aggregator

![Version](https://img.shields.io/badge/version-v0.1.0-blue)
![CI](https://github.com/flyspark015/ndefender-backend-aggregator/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-proprietary-red)
![Production](https://img.shields.io/badge/production-GREEN-2ea043)

A production-grade unified control plane that ingests all N-Defender subsystems and exposes a single REST + WebSocket API to the GUI. JSONL logs are the ground truth. WebSocket is the fast path for responsiveness.

## 🔄 Event Flow (High-Level)

```
   JSONL / Serial / REST
            │
            ▼
       Ingestion
            │
            ▼
       State Store
            │
            ├─ REST Snapshot (/api/v1/status)
            └─ WS Fast Path (/api/v1/ws)
```

## 📡 Subsystem Integration Map

| Subsystem | Input | Ground Truth | Output | Notes |
|---|---|---|---|---|
| AntSDR | JSONL | ✅ | RF_CONTACT_* | Rotation-safe tailing |
| RemoteID | JSONL | ✅ | CONTACT_* / TELEMETRY_UPDATE / REPLAY_STATE | Timestamp normalized |
| ESP32 Panel | Serial JSON | ❌ | ESP32_TELEMETRY / COMMAND_ACK | Robust framing + retries |
| System Controller | REST | ❌ | SYSTEM_UPDATE / UPS_UPDATE / NETWORK_UPDATE / AUDIO_UPDATE | Polling | 

## 🧠 Unified Contact Model
The UI consumes a single merged contact list:
- `REMOTE_ID` (from RemoteID engine)
- `RF` (from AntSDR)
- `FPV` (from ESP32 telemetry)

Sorted by severity → distance (if provided) → last_seen_ts.

## 📊 JSONL Ground Truth
JSONL feeds from AntSDR and RemoteID are authoritative. The aggregator tails these logs with rotation/truncation safety and rebuilds state on restart.

## ⚡ WebSocket Fast Path
WebSocket emits normalized event envelopes for low-latency UI updates. REST remains the snapshot source of truth.

## 🔐 Security Model
- API Key authentication (`X-API-Key`) enforced by default.
- RBAC (`X-Role`) with `viewer`, `operator`, `admin` roles.

## 🚨 Safety Model
- Reboot/shutdown are disabled by default.
- `confirm=true` required for unsafe operations.
- Command endpoints are rate limited.

## 🔄 Command Routing
Commands flow: REST → Router → Subsystem → ACK → WS
- ESP32 commands mapped to serial protocol.
- System controller commands mapped to REST endpoints.

## 🟢 Production Ready
The repository is GREEN, tested, and release-locked. Runtime logic is frozen for v0.1.0.

## 🧪 GREEN Verification Checklist
- ✅ `ruff check .`
- ✅ `pytest`
- ✅ All subsystems integrated
- ✅ Release tag present: `v0.1.0`

## 🔍 Documentation Index
- `docs/ARCHITECTURE.md` — System design and data flow
- `docs/API.md` — REST + WS contract
- `docs/SECURITY.md` — Security model and best practices
- `docs/OPERATIONS.md` — Operator handbook
- `docs/CONFIGURATION.md` — Full config reference

## 🏷 Release
- Version: v0.1.0
- Status: GREEN
- Date: 2026-02-15
- CI: Passing
- Tests: Passing
- Production Lock: Enabled
