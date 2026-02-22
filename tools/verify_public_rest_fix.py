#!/usr/bin/env python3
"""Verify Cloudflare 1010 block removed for public REST."""

from __future__ import annotations

import argparse
import subprocess
import sys
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def run(cmd: list[str]) -> int:
    print(f"$ {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=False, text=True)
        return result.returncode
    except FileNotFoundError as exc:
        print(f"error: {exc}")
        return 1


def urllib_probe(url: str) -> int:
    print(f"\nPython urllib GET (no UA): {url}")
    req = Request(url, method="GET")
    try:
        with urlopen(req, timeout=10) as resp:
            body = resp.read(120)
            print(f"status {resp.status}")
            print(f"server {resp.headers.get('server')}")
            print(f"body {body!r}")
            return 0 if resp.status == 200 else 2
    except HTTPError as err:
        body = err.read(120)
        print(f"status {err.code}")
        print(f"server {err.headers.get('server')}")
        print(f"body {body!r}")
        return 2
    except Exception as err:
        print(f"error: {err}")
        return 3


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="https://n.flyspark.in/api/v1")
    args = parser.parse_args()

    base = args.base.rstrip("/")
    health = f"{base}/health"

    rc = 0
    rc |= run(["curl", "-i", health])
    rc |= urllib_probe(health)
    rc |= run(["python3", "tools/run_full_diagnostics.py", "--base", base])

    return 0 if rc == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
