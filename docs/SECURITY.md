# Security 🔐

Why this exists: It defines the security posture, storage best practices, and safe evolution path for future auth mechanisms.

## API Key Storage Best Practices
- Never commit keys to git.
- Store in environment variables or secure config management.
- Rotate keys whenever operator devices change.

## Reverse Proxy Recommendation
- Deploy behind Nginx or Caddy for TLS termination.
- Enforce IP allowlists or VPN at the proxy layer.

## Role Separation Recommendation
- Viewer for read-only dashboards.
- Operator for tuning/scanning/video control.
- Admin for reboot/shutdown and unsafe operations.

## Unsafe Operations Disabled by Default
- Reboot/shutdown are blocked unless explicitly enabled.
- `confirm=true` required for all unsafe actions.

## Future JWT Migration Path
- Keep `X-API-Key` for local deployments.
- Introduce JWT auth behind reverse proxy without breaking REST routes.
- RBAC can be embedded in JWT claims when enabled.

