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
                first_type = json.loads(msgs[0]).get("type")
            except Exception:
                first_type = None
            print(f"received={len(msgs)}, first_type={first_type}")
        else:
            print("received=0")
        if len(msgs) < 3:
            print("FAIL: expected >=3 messages in window")
            sys.exit(1)
        print("PASS: received >=3 messages")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=os.environ.get("WS_URL", "wss://n.flyspark.in/api/v1/ws"))
    parser.add_argument("--origin", default=os.environ.get("WS_ORIGIN", "https://www.figma.com"))
    parser.add_argument("--seconds", type=int, default=10)
    args = parser.parse_args()
    asyncio.run(run(args.url, args.origin, args.seconds))


if __name__ == "__main__":
    main()
