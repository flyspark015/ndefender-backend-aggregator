# ROADMAP 🗺️

Why this exists: This roadmap keeps delivery phased, testable, and auditable so integration work stays aligned with safety and uptime requirements.

## Phases
- [ ] Phase 1: Skeleton + Auth + CI
  - Establish FastAPI service, config loader, auth, RBAC, and baseline CI.
- [ ] Phase 2: State Core + WS
  - Central async state store and WebSocket broadcast manager.
- [ ] Phase 3: System Controller Integration
  - Poll System Controller for UPS/system/network/audio status.
- [ ] Phase 4: ESP32 Serial Integration
  - Robust serial bridge for telemetry and command ACK.
- [ ] Phase 5: AntSDR JSONL Reader
  - Rotation-safe JSONL tailing for RF events.
- [ ] Phase 6: RemoteID JSONL Reader
  - Normalized RemoteID events into canonical state.
- [ ] Phase 7: Canonical Contact Model
  - Unified contacts view merged across subsystems.
- [ ] Phase 8: Command Routing Layer
  - Safe, audited routing to subsystems.
- [ ] Phase 9: Hardening + Rate Limiting
  - Reliability, retries, safety gates, and operational guardrails.
- [ ] Phase 10: GREEN Lock + Release Tag
  - Final validation, CI green, and tagged release.
