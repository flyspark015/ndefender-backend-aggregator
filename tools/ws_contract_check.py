"""Validate WS event envelopes against allowed types."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable

ALLOWED_TYPES = {
    "SYSTEM_STATUS",
    "CONTACT_NEW",
    "CONTACT_UPDATE",
    "CONTACT_LOST",
    "RF_CONTACT_NEW",
    "RF_CONTACT_UPDATE",
    "RF_CONTACT_LOST",
    "TELEMETRY_UPDATE",
    "REPLAY_STATE",
    "NETWORK_UPDATE",
    "AUDIO_UPDATE",
    "UPS_UPDATE",
    "ESP32_TELEMETRY",
    "COMMAND_ACK",
    "LOG_EVENT",
    "SYSTEM_UPDATE",
}

REQUIRED_KEYS = {"type", "timestamp_ms", "source", "data"}


def iter_lines(paths: Iterable[str]) -> Iterable[str]:
    for path in paths:
        with open(path, encoding="utf-8") as handle:
            for raw_line in handle:
                stripped = raw_line.strip()
                if stripped:
                    yield stripped


def validate_line(line: str) -> tuple[bool, str]:
    try:
        payload = json.loads(line)
    except json.JSONDecodeError as exc:
        return False, f"invalid json: {exc}"
    if not isinstance(payload, dict):
        return False, "payload must be object"
    missing = REQUIRED_KEYS - payload.keys()
    if missing:
        return False, f"missing keys: {sorted(missing)}"
    if payload["type"] not in ALLOWED_TYPES:
        return False, f"invalid type: {payload['type']}"
    if not isinstance(payload["timestamp_ms"], int):
        return False, "timestamp_ms must be int"
    return True, "ok"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", help="JSONL files to validate")
    args = parser.parse_args()

    errors = 0
    for line in iter_lines(args.paths):
        ok, message = validate_line(line)
        if not ok:
            errors += 1
            print(message)

    if errors:
        print(f"FAIL: {errors} invalid events")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
