"""In-memory rate limiting utilities."""

from __future__ import annotations

import asyncio
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status

from .config import get_config


class RateLimiter:
    def __init__(self) -> None:
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def enforce(self, key: str, limit: int, window_seconds: int) -> None:
        now = time.time()
        async with self._lock:
            bucket = self._hits[key]
            while bucket and now - bucket[0] > window_seconds:
                bucket.popleft()
            if len(bucket) >= limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded",
                )
            bucket.append(now)


_rate_limiter = RateLimiter()


def _client_key(request: Request) -> str:
    if request.client:
        return request.client.host
    return "unknown"


async def dangerous_rate_limit(request: Request) -> None:
    config = get_config()
    await _rate_limiter.enforce(
        _client_key(request),
        config.rate_limits.dangerous_per_minute,
        60,
    )


async def command_rate_limit(request: Request) -> None:
    config = get_config()
    await _rate_limiter.enforce(
        _client_key(request),
        config.rate_limits.command_per_minute,
        60,
    )
