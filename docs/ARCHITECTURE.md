# Architecture 🧭

Why this exists: It documents system boundaries, data flow, and failure isolation so integrations stay correct as the platform evolves.

## Core Principles
- **Ground truth first:** JSONL feeds are authoritative.
- **Fast path updates:** WebSocket stream for UI responsiveness.
- **Snapshot access:** REST endpoints provide current state on demand.

## Components
- **Ingestion layer:** JSONL tailers, serial bridge, system controller poller.
- **State layer:** Central async store with canonical schema.
- **Event bus:** Internal publisher/subscriber channel for decoupled ingestion and WS broadcast.
- **API layer:** FastAPI with REST + WebSocket endpoints.
- **Security layer:** API key auth, RBAC, rate limiting.

## Data Flow
1. Subsystems emit JSONL/serial/REST data.
2. Ingestion normalizes events.
3. State store updates canonical snapshot.
4. WebSocket broadcasts deltas or snapshots.
5. REST endpoints serve latest snapshot.

## Failure Isolation
- Each integration runs independently so partial failures do not block the API.
- Restart-safe JSONL tailing ensures no data loss after service restarts.
