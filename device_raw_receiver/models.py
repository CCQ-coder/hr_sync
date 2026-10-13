"""Stable types shared by the raw receiver components."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class SessionStatus(str, Enum):
    """The terminal and non-terminal states recorded for a TCP connection."""

    OPEN = "open"
    CLOSED = "closed"
    CLOSED_ABNORMALLY = "closed_abnormally"
    IDLE_TIMEOUT = "idle_timeout"
    INTERRUPTED = "interrupted"


@dataclass(frozen=True)
class PersistedChunk:
    """A byte range that is safely present in a raw payload segment."""

    session_id: str
    segment_name: str
    offset: int
    length: int
    path: Path
