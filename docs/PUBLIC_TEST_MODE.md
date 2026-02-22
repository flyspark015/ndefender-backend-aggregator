# PUBLIC_TEST_MODE (Test-Only)

**WARNING:** This mode disables all auth and origin restrictions. Use ONLY for short-lived public tests.

## Enable
Set the environment variable on the backend service and restart:
```bash
sudo mkdir -p /etc/systemd/system/ndefender-backend.service.d
cat <<'EOT' | sudo tee /etc/systemd/system/ndefender-backend.service.d/override.conf >/dev/null
[Service]
Environment=PUBLIC_TEST_MODE=true
EOT
sudo systemctl daemon-reload
sudo systemctl restart ndefender-backend
```

## Disable (Revert)
Remove or set the flag to false, then restart:
```bash
sudo rm -f /etc/systemd/system/ndefender-backend.service.d/override.conf
sudo systemctl daemon-reload
sudo systemctl restart ndefender-backend
```

## Behavior When Enabled
- No API keys, no auth, no RBAC enforcement
- CORS allows all origins (`*`)
- Allowed methods: `GET, POST, OPTIONS`
- Allowed headers: `Content-Type, X-API-Key, X-Role`
- WebSocket accepts all origins (or missing Origin)

## Risks
- Anyone on the internet can call the API and WebSocket.
- Data exposure and control actions are possible.

## Revert to Localhost-Only
Disable public exposure by stopping the Cloudflare tunnel:
```bash
sudo systemctl disable --now cloudflared
```

Re-enable later with:
```bash
sudo systemctl enable --now cloudflared
```
