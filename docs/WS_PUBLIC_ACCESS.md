# WebSocket Public Access

Endpoint: `wss://n.flyspark.in/api/v1/ws`

## Origin Enforcement
WebSocket handshake enforces `Origin` against the same CORS allow list:
- `https://www.figma.com`
- `https://figma.com`
- `^https://([a-z0-9-]+\.)*figma\.com$`

Clients must send an allowed `Origin` header.

## Python Test (wss)
```bash
python3 - <<'PY'
import asyncio
import json

import websockets

async def main():
    async with websockets.connect(
        "wss://n.flyspark.in/api/v1/ws",
        extra_headers={"Origin": "https://www.figma.com"},
    ) as ws:
        msg = await ws.recv()
        print(msg)
        # Basic sanity parse
        try:
            print(json.loads(msg).get("type"))
        except Exception:
            pass

asyncio.run(main())
PY
```

If `websockets` is missing:
```bash
python3 -m pip install --user websockets
```
