# Command Routing 🧭

Why this exists: It defines the contract and routing expectations for command execution without coupling to any subsystem implementation.

## Command Flow
1. API receives a command request.
2. Router selects the first handler that can process the command.
3. Handler returns a `CommandResult` with a tracking ID.

## Contract Types
- `CommandRequest`: normalized input for all command handlers.
- `CommandHandler`: interface implemented by subsystems.
- `CommandRouter`: dispatches requests to handlers.

## Reliability Expectations
- Handlers must return a result even on failure.
- Router must remain non-blocking if a handler fails.
- Commands must be auditable via IDs and timestamps.

## ESP32 Mappings
- `vrx/tune` → `SET_VRX_FREQ`
- `scan/start` → `START_SCAN`
- `scan/stop` → `STOP_SCAN`
- `video/select` → `VIDEO_SELECT`

## System Controller Mappings
- `system/reboot` → `POST /api/v1/system/reboot`
- `system/shutdown` → `POST /api/v1/system/shutdown`
- `services/restart` → `POST /api/v1/services/{name}/restart`
