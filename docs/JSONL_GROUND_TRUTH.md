# JSONL Ground Truth 📜

Why this exists: It defines the authoritative event streams that back the system state and ensures restart-safe behavior.

## Sources
- AntSDR JSONL events
- RemoteID JSONL events

## Reliability Requirements
- Tailing must handle truncation and rotation.
- Partial lines must be buffered until complete.
- Service restarts must re-open and continue without data loss.

