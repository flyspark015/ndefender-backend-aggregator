#!/usr/bin/env python3
import asyncio
import json
import sys
import websockets

URL = "ws://127.0.0.1:8000/api/v1/ws"

async def main():
    try:
        async with websockets.connect(URL) as ws:
            print("connected")
            msg = await asyncio.wait_for(ws.recv(), timeout=10)
            print("received=1")
            print("first_200=", msg[:200])
            try:
                data = json.loads(msg)
                print("first_type=", data.get("type"))
            except Exception:
                print("first_type=unknown")
    except Exception as exc:
        print("error", exc)
        sys.exit(2)

if __name__ == "__main__":
    asyncio.run(main())
