# Deployment 🚀

Why this exists: It records environment assumptions, service setup, and operational steps required for reliable installs.

## Targets
- Raspberry Pi 5 (Debian 12 Bookworm)
- Python 3.11+

## Service Expectations
- Run as a systemd unit.
- Persist logs to `/opt/ndefender/logs`.
- Maintain access to JSONL ground-truth files.

## Configuration
- Default config: `config/default.yaml`.
- Override via `NDEFENDER_CONFIG` for production or site-specific settings.

