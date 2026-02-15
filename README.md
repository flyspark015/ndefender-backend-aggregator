# N-Defender Backend Aggregator 🛡️

Why this exists: This service unifies all N-Defender subsystems behind a single, secure API surface so the GUI and operators have one authoritative source of truth.

## Scope ✨
- Ingests subsystem data (JSONL, serial, REST/WS)
- Normalizes into a canonical state model
- Serves REST + WebSocket APIs for the GUI

## Configuration ⚙️
Configuration is centralized in `config/default.yaml` with optional environment-specific overrides. See `docs/CONFIGURATION.md` for full details.

## Status 🚧
- Phase 1 in progress (skeleton + auth + CI)

