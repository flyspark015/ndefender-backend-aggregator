"""Rotation-safe JSONL tailer."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TailStats:
    lines: int = 0
    bytes_read: int = 0
    resets: int = 0


class JsonlTailer:
    def __init__(self, path: str, poll_interval_ms: int) -> None:
        self._path = Path(path)
        self._poll_interval = poll_interval_ms / 1000
        self._offset = 0
        self._inode: int | None = None
        self._mtime_ns: int | None = None
        self._ctime_ns: int | None = None
        self._buffer = ""
        self._stats = TailStats()

    @property
    def stats(self) -> TailStats:
        return self._stats

    async def tail(self) -> AsyncIterator[str]:
        while True:
            await self._wait()
            if not self._path.exists():
                continue
            try:
                stat = self._path.stat()
            except FileNotFoundError:
                continue
            mtime_ns = getattr(stat, "st_mtime_ns", int(stat.st_mtime * 1_000_000_000))
            ctime_ns = getattr(stat, "st_ctime_ns", int(stat.st_ctime * 1_000_000_000))
            if self._inode is None or self._inode != stat.st_ino:
                self._inode = stat.st_ino
                self._mtime_ns = mtime_ns
                self._ctime_ns = ctime_ns
                self._offset = 0
                self._buffer = ""
                self._stats.resets += 1
            if stat.st_size < self._offset:
                self._offset = 0
                self._buffer = ""
                self._stats.resets += 1
            if (
                self._mtime_ns is not None
                and self._ctime_ns is not None
                and (mtime_ns != self._mtime_ns or ctime_ns != self._ctime_ns)
                and stat.st_size <= self._offset
            ):
                self._offset = 0
                self._buffer = ""
                self._stats.resets += 1
            self._mtime_ns = mtime_ns
            self._ctime_ns = ctime_ns
            async for line in self._read_new_lines():
                yield line

    async def _read_new_lines(self) -> AsyncIterator[str]:
        if not self._path.exists():
            return
        with self._path.open("r", encoding="utf-8") as handle:
            handle.seek(self._offset)
            data = handle.read()
            if not data:
                return
            self._stats.bytes_read += len(data)
            self._offset = handle.tell()
            self._buffer += data
            while "\n" in self._buffer:
                line, _, rest = self._buffer.partition("\n")
                self._buffer = rest
                cleaned = line.strip()
                if cleaned:
                    self._stats.lines += 1
                    yield cleaned

    async def _wait(self) -> None:
        await asyncio.sleep(self._poll_interval)


async def simulate_append(path: str, lines: list[str]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as handle:
        for line in lines:
            handle.write(line + "\n")


def force_rotate(path: str) -> None:
    p = Path(path)
    if not p.exists():
        return
    rotated = p.with_suffix(p.suffix + ".1")
    if rotated.exists():
        rotated.unlink()
    p.rename(rotated)
    p.touch()


def truncate_file(path: str) -> None:
    p = Path(path)
    if not p.exists():
        return
    with p.open("w", encoding="utf-8") as handle:
        handle.truncate(0)
