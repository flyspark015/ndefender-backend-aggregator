# Configuration 🧩

Why this exists: This document defines every configuration section so deployments stay consistent, secure, and repeatable across environments.

## File Locations
- `config/default.yaml` is the baseline for production and must be kept current.
- `config/development.yaml` is an example override for local development.

## Sections

### system_controller
- `base_url`: Base URL for the System Controller API.
- `timeout_seconds`: Per-request timeout in seconds.

### esp32
- `serial_port`: Path to the ESP32 serial device.
- `baud_rate`: Serial baud rate.
- `reconnect_delay_seconds`: Delay before retrying connection.

### antsdr
- `jsonl_path`: Path to AntSDR JSONL ground-truth log.
- `tail_poll_interval_ms`: Poll interval for tailer.

### remoteid
- `jsonl_path`: Path to RemoteID JSONL ground-truth log.
- `tail_poll_interval_ms`: Poll interval for tailer.

### auth
- `api_key_required`: Enforce `X-API-Key` when true.
- `api_key`: Shared API key for GUI and tooling.
- `rbac_enabled`: Enables role-based access control checks.

### rbac
- `roles`: Role definitions and permissions.
- `permissions`: Allowed actions for each role.

### safety
- `allow_unsafe_operations`: Global switch for dangerous actions.
- `reboot_cooldown_seconds`: Cooldown between reboots.
- `shutdown_cooldown_seconds`: Cooldown between shutdowns.

### polling
- `system_controller_interval_ms`: Polling interval for system controller status.
- `ups_interval_ms`: Polling interval for UPS telemetry.
- `network_interval_ms`: Polling interval for network status.
- `audio_interval_ms`: Polling interval for audio status.

### logging
- `level`: Logging verbosity.

### rate_limits
- `dangerous_per_minute`: Rate limit for unsafe endpoints.
- `command_per_minute`: Rate limit for standard command endpoints.

### features
- `enable_antsdr`: Toggle AntSDR ingestion.
- `enable_remoteid`: Toggle RemoteID ingestion.
- `enable_esp32`: Toggle ESP32 serial ingestion.

## Environment Overrides
To override defaults, set an explicit config file path:

```bash
export NDEFENDER_CONFIG=/opt/ndefender/config/production.yaml
```

The override file is merged on top of `config/default.yaml`. Only the keys you set are changed.

## Security Notes 🔐
- Never commit real API keys to git.
- Keep `api_key_required` enabled in production.
- Rotate `api_key` when operators or devices change.

## Switching Environments
- Development: set `NDEFENDER_CONFIG` to a local override file.
- Production: maintain a secure, host-local config and point `NDEFENDER_CONFIG` to it.
