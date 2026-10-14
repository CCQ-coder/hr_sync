"""Application logging that never includes raw device payload content."""

from __future__ import annotations

import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


def configure_application_logger(storage_root: Path) -> logging.Logger:
    """Create the receiver's daily UTF-8 application logger."""
    logger = logging.getLogger("device_raw_receiver")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    log_path = Path(storage_root) / "logs" / "receiver.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_path = str(log_path.resolve())
    if any(getattr(handler, "baseFilename", None) == resolved_path for handler in logger.handlers):
        return logger
    handler = TimedRotatingFileHandler(
        resolved_path,
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
        utc=True,
    )
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    logger.addHandler(handler)
    return logger
