"""Utility to exercise JSONL tailer behavior."""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from ndefender_backend_aggregator.ingest.jsonl_tail import JsonlTailer, force_rotate


async def run(path: str) -> None:
    tailer = JsonlTailer(path, poll_interval_ms=200)
    async for line in tailer.tail():
        print(line)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--rotate", action="store_true")
    args = parser.parse_args()

    if args.rotate:
        force_rotate(args.path)
        Path(args.path).write_text(json.dumps({"type": "CONTACT_UPDATE"}) + "\n")

    asyncio.run(run(args.path))


if __name__ == "__main__":
    main()
