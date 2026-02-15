# Architecture 🧭

Why this exists: It documents the system boundaries, data flow, and failure isolation so integrations stay correct as the platform evolves.

## Overview
- Hybrid ingestion: JSONL ground truth, WS fast path, REST snapshot
- Central async state store with canonical models
- Integration modules per subsystem

