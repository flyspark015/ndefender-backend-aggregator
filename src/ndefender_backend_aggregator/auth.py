"""API key authentication."""

from __future__ import annotations

from fastapi import Header, HTTPException, status

from .config import get_config


def api_key_auth(x_api_key: str | None = Header(default=None)) -> None:
    config = get_config()
    if not config.auth.api_key_required:
        return
    if not x_api_key or x_api_key != config.auth.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
