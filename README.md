# N-Defender Backend Aggregator 🛡️

Why this exists: This service unifies all N-Defender subsystems behind a single, secure API surface so the GUI and operators have one authoritative source of truth.

## Scope ✨
- Ingests subsystem data (JSONL, serial, REST/WS)
- Normalizes into a canonical state model
- Serves REST + WebSocket APIs for the GUI

## Architecture Snapshot 🧭
- **Ground truth:** JSONL feeds from AntSDR and RemoteID
- **Fast path:** WebSocket updates for UI responsiveness
- **Control plane:** REST endpoints for snapshots and commands

## Configuration ⚙️
Configuration is centralized in `config/default.yaml` with optional environment-specific overrides. See `docs/CONFIGURATION.md` for full details.

## Security Posture 🔐
- API key authentication from day one
- RBAC roles for operator separation
- Rate limits on dangerous operations

## Operations ✅
Operational checklists and recovery steps are in `docs/OPERATIONS.md`.

## Status 🚧
- Foundation phase in progress
