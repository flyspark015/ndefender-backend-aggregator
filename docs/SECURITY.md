# Security 🔐

Why this exists: It defines the security posture for a deployment with no auth headers required and explains how to harden the perimeter.

## Current Auth Posture (No Auth Required)
- The API accepts requests without `X-API-Key` or role headers.
- Safety controls still apply to dangerous operations (`confirm=true`, cooldowns).

## Reverse Proxy Recommendation
- Deploy behind Nginx or Caddy for TLS termination.
- Enforce IP allowlists or VPN at the proxy layer.

## Role Separation (Future Option)
- If auth is reintroduced later, roles can be mapped to read vs control.

## Unsafe Operations Disabled by Default
- Reboot/shutdown are blocked unless explicitly enabled.
- `confirm=true` required for all unsafe actions.

## Future JWT Migration Path
- Introduce JWT behind a reverse proxy without changing routes.
- Embed role claims only if access control becomes necessary.
