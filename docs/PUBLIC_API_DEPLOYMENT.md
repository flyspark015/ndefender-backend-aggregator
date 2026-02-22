# Public API Deployment (Cloudflare Tunnel)

Goal: Expose the Backend Aggregator at `https://n.flyspark.in` with WSS at `wss://n.flyspark.in/api/v1/ws` using Cloudflare Tunnel, without opening router ports.

## Prereqs
- Domain `flyspark.in` is managed in Cloudflare DNS.
- Backend Aggregator is reachable on the Pi at `http://127.0.0.1:8000`.
- `cloudflared` installed on the Pi.

## Install cloudflared (Debian/arm64)
```bash
curl -L -o /tmp/cloudflared-linux-arm64.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb
sudo dpkg -i /tmp/cloudflared-linux-arm64.deb
cloudflared --version
```

## Authenticate to Cloudflare
```bash
cloudflared tunnel login
```
Follow the URL printed in the terminal and authorize the `flyspark.in` zone.

## Create Tunnel + DNS Route
```bash
cloudflared tunnel create ndefender-api
cloudflared tunnel route dns ndefender-api n.flyspark.in
```
Capture the tunnel UUID from the `create` command output.

## Configure Tunnel
```bash
sudo mkdir -p /etc/cloudflared
sudo cp ~/.cloudflared/<TUNNEL-UUID>.json /etc/cloudflared/
```
Create `/etc/cloudflared/config.yml`:
```yaml
tunnel: <TUNNEL-UUID>
credentials-file: /etc/cloudflared/<TUNNEL-UUID>.json

ingress:
  - hostname: n.flyspark.in
    service: http://127.0.0.1:8000
  - service: http_status:404
```

## Systemd Service (Autostart)
```bash
sudo cloudflared service install
sudo systemctl enable --now cloudflared
sudo systemctl status cloudflared --no-pager
```

## Health Checks
```bash
curl -I https://n.flyspark.in/api/v1/health
curl https://n.flyspark.in/api/v1/status
journalctl -u cloudflared -n 100 --no-pager
```

## Rate-Limit Protection (Cloudflare Edge)
Use Cloudflare WAF/Rate Limiting to protect `/api/v1/*`:
- Example rule: `http.request.uri.path starts_with "/api/v1/"`
- Start with a conservative limit (e.g., 120 requests/min per IP) and tune.

## Rollback
```bash
sudo systemctl disable --now cloudflared
sudo rm -f /etc/cloudflared/config.yml /etc/cloudflared/<TUNNEL-UUID>.json
cloudflared tunnel route dns ndefender-api n.flyspark.in --delete
cloudflared tunnel delete ndefender-api
```

## Notes
- TLS is handled by Cloudflare; no certs required on the Pi.
- WebSockets are supported through Cloudflare Tunnel by default.
- CORS for browser clients is enforced by the backend config (see `docs/CORS.md`).
