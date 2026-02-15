# Security 🔐

Why this exists: It captures authentication, authorization, and safety controls required for secure deployment.

## Authentication
- API key required via `X-API-Key` by default.
- Disable only in local or isolated environments.

## Authorization (RBAC)
- Roles: `viewer`, `operator`, `admin`.
- Permissions map to read and control surfaces.
- Enforced via `X-Role` when enabled.

## Rate Limiting
- Command endpoints are throttled to prevent unsafe bursts.
- Dangerous operations are rate limited more strictly.

## Unsafe Operations
- Reboot/shutdown gated by configuration and explicit confirmation.
- Cooldowns prevent repeated execution in short windows.

