#!/usr/bin/env python3
import asyncio
import json
import os

import websockets


async def main() -> None:
    url = os.environ.get("WS_URL", "wss://n.flyspark.in/api/v1/ws")
    origin = os.environ.get("WS_ORIGIN")
    headers = {"Origin": origin} if origin else None

    async with websockets.connect(url, extra_headers=headers) as ws:
        print("connected")
        msg = await ws.recv()
        print(f"first_200={msg[:200]}")
        first_type = None
        try:
            first_type = json.loads(msg).get("type")
        except Exception:
            first_type = None
        print(f"received=1, first_type={first_type}")


if __name__ == "__main__":
    asyncio.run(main())
