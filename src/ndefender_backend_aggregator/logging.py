"""Structured logging setup."""

from __future__ import annotations

import logging


def configure_logging(level: str) -> None:
    """Configure process-wide logging."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
