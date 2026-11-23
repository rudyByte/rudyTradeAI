from __future__ import annotations

import logging


def configure_logging(level: str = "INFO") -> None:
    """Configure safe console logging without secrets or credential values."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
