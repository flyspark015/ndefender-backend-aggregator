import asyncio
import json
import time
from pathlib import Path

import pytest

from ndefender_backend_aggregator.ingest.jsonl_tail import JsonlTailer, force_rotate, truncate_file


async def wait_for_lines(lines: list[str], expected: int, timeout_s: float = 1.0) -> None:
    start = time.monotonic()
    while len(lines) < expected:
        if time.monotonic() - start > timeout_s:
            raise AssertionError("Timed out waiting for lines")
        await asyncio.sleep(0.01)


@pytest.mark.asyncio
async def test_jsonl_tailer_rotation(tmp_path: Path):
    expected_count = 2
    path = tmp_path / "events.jsonl"
    path.write_text(json.dumps({"type": "CONTACT_NEW"}) + "\n")

    tailer = JsonlTailer(str(path), poll_interval_ms=10)
    lines = []

    async def collect():
        async for line in tailer.tail():
            lines.append(line)
            if len(lines) == expected_count:
                break

    task = asyncio.create_task(collect())
    await wait_for_lines(lines, 1)
    force_rotate(str(path))
    path.write_text(json.dumps({"type": "CONTACT_UPDATE"}) + "\n")
    await wait_for_lines(lines, expected_count)
    if not task.done():
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    assert any("CONTACT_NEW" in line for line in lines)
    assert any("CONTACT_UPDATE" in line for line in lines)


@pytest.mark.asyncio
async def test_jsonl_tailer_truncation(tmp_path: Path):
    expected_count = 2
    path = tmp_path / "events.jsonl"
    path.write_text(json.dumps({"type": "CONTACT_NEW"}) + "\n")

    tailer = JsonlTailer(str(path), poll_interval_ms=10)
    lines = []

    async def collect():
        async for line in tailer.tail():
            lines.append(line)
            if len(lines) == expected_count:
                break

    task = asyncio.create_task(collect())
    await wait_for_lines(lines, 1)
    truncate_file(str(path))
    await asyncio.sleep(0.05)
    path.write_text(json.dumps({"type": "CONTACT_LOST"}) + "\n")
    await wait_for_lines(lines, expected_count)
    if not task.done():
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    assert any("CONTACT_NEW" in line for line in lines)
    assert any("CONTACT_LOST" in line for line in lines)
