# ROADMAP 🗺️

Why this exists: This roadmap keeps delivery phased, testable, and auditable so integration work stays aligned with safety and uptime requirements.

## Phases
- [x] Phase 1: Skeleton + Auth + CI
  - Establish FastAPI service, config loader, auth, RBAC, and baseline CI.
- [x] Phase 2: State Core + WS
  - Central async state store and WebSocket broadcast manager.
- [x] Phase 3: System Controller Integration
  - Poll System Controller for UPS/system/network/audio status.
- [x] Phase 4: ESP32 Serial Integration
  - Robust serial bridge for telemetry and command ACK.
- [x] Phase 5: AntSDR JSONL Reader
  - Rotation-safe JSONL tailing for RF events.
- [x] Phase 6: RemoteID JSONL Reader
  - Normalized RemoteID events into canonical state.
- [x] Phase 7: Canonical Contact Model
  - Unified contacts view merged across subsystems.
- [x] Phase 8: Command Routing Layer
  - Safe, audited routing to subsystems.
- [x] Phase 9: Hardening + Rate Limiting
  - Reliability, retries, safety gates, and operational guardrails.
- [x] Phase 10: GREEN Lock + Release Tag
  - Final validation, CI green, and tagged release.
- [ ] Phase 11: Public API Exposure (Cloudflare Tunnel + CORS)
  - Cloudflare Tunnel, CORS policy, and public WSS verification.
