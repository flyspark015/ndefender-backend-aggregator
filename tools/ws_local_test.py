#!/usr/bin/env python3
import argparse
import asyncio
import json
import os
import sys
import time

import websockets


async def run(url: str, origin: str | None, seconds: int) -> None:
    headers = {"Origin": origin} if origin else None
    try:
        async with websockets.connect(url, extra_headers=headers) as ws:
            print("connected")
            msgs = []
            start = time.time()
            while time.time() - start < seconds and len(msgs) < 10:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=seconds - (time.time() - start))
                    msgs.append(msg)
                except asyncio.TimeoutError:
                    break
            if msgs:
                print(f"first_200={msgs[0][:200]}")
                try:
                    data = json.loads(msgs[0])
                    print("first_type=", data.get("type"))
                except Exception:
                    print("first_type=unknown")
                print(f"received={len(msgs)}")
            else:
                print("received=0")
    except Exception as exc:
        print("error", exc)
        sys.exit(2)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=os.environ.get("WS_URL", "ws://127.0.0.1:8001/api/v1/ws"))
    parser.add_argument("--origin", default=os.environ.get("WS_ORIGIN", "https://www.figma.com"))
    parser.add_argument("--seconds", type=int, default=10)
    args = parser.parse_args()
    asyncio.run(run(args.url, args.origin, args.seconds))


if __name__ == "__main__":
    main()
