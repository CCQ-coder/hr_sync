"""Byte-exact session archive creation, finalization, and recovery."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .models import PersistedChunk, SessionStatus


_PAYLOAD_NAME = re.compile(r"payload-\d{6}\.bin\Z")
_LOGGER = logging.getLogger(__name__)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _write_json_atomically(path: Path, content: Dict[str, object]) -> None:
    temporary_path = path.with_name(".{0}.tmp".format(path.name))
    with temporary_path.open("w", encoding="utf-8", newline="\n") as output:
        json.dump(content, output, ensure_ascii=False, indent=2, sort_keys=True)
        output.write("\n")
        output.flush()
        os.fsync(output.fileno())
    os.replace(str(temporary_path), str(path))


def _append_event(path: Path, event: Dict[str, object], fsync: bool) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as output:
        output.write(json.dumps(event, ensure_ascii=False, sort_keys=True))
        output.write("\n")
        output.flush()
        if fsync:
            os.fsync(output.fileno())


class SessionArchive:
    """The lossless disk representation of one accepted TCP connection."""

    def __init__(
        self,
        session_id: str,
        session_dir: Path,
        metadata: Dict[str, object],
        segment_max_bytes: int,
        fsync_policy: str,
    ) -> None:
        self.session_id = session_id
        self.session_dir = session_dir
        self._metadata = metadata
        self._segment_max_bytes = segment_max_bytes
        self._fsync_policy = fsync_policy
        self._events_path = session_dir / "events.jsonl"
        self._segment_file = None
        self._segment_path: Optional[Path] = None
        self._segment_size = 0
        self._segment_number = 0
        self._event_sequence = 0
        self._rotate_before_next_append = False
        self._hasher = hashlib.sha256()
        self._total_bytes = 0
        self._segments: List[Dict[str, object]] = []
        self._closed = False

    @classmethod
    def create(
        cls,
        storage_root: Path,
        local_host: str,
        local_port: int,
        peer_host: str,
        peer_port: int,
        segment_max_bytes: int,
        fsync_policy: str,
    ) -> "SessionArchive":
        """Create an open session directory without interpreting socket bytes."""
        now = datetime.now(timezone.utc)
        session_id = str(uuid.uuid4())
        session_dir = Path(storage_root) / "incoming" / now.strftime("%Y") / now.strftime("%m") / now.strftime("%d") / session_id
        session_dir.mkdir(parents=True, exist_ok=False)
        metadata: Dict[str, object] = {
            "schema_version": 1,
            "session_id": session_id,
            "status": SessionStatus.OPEN.value,
            "started_at": _utc_now(),
            "ended_at": None,
            "local": {"host": local_host, "port": local_port},
            "peer": {"host": peer_host, "port": peer_port},
            "total_bytes": 0,
            "segments": [],
            "sha256": None,
        }
        archive = cls(session_id, session_dir, metadata, segment_max_bytes, fsync_policy)
        archive._save_metadata()
        archive._record_event("connected", local=metadata["local"], peer=metadata["peer"])
        return archive

    def append(self, data: bytes) -> PersistedChunk:
        """Append one complete receive buffer without inserting or splitting bytes."""
        if self._closed:
            raise RuntimeError("不能向已关闭会话追加数据")
        if not isinstance(data, bytes) or not data:
            raise ValueError("归档数据必须是非空 bytes")
        if self._rotate_before_next_append:
            self._close_segment()
            self._open_segment()
            self._rotate_before_next_append = False
        elif self._segment_file is None:
            self._open_segment()

        offset = self._segment_size
        self._segment_file.write(data)
        self._segment_size += len(data)
        self._total_bytes += len(data)
        self._hasher.update(data)
        self._segments[-1]["bytes"] = self._segment_size
        if self._fsync_policy == "always":
            self._segment_file.flush()
            os.fsync(self._segment_file.fileno())

        chunk = PersistedChunk(
            session_id=self.session_id,
            segment_name=self._segment_path.name,
            offset=offset,
            length=len(data),
            path=self._segment_path,
        )
        self._record_event(
            "data_persisted",
            segment=chunk.segment_name,
            offset=chunk.offset,
            length=chunk.length,
        )
        if self._segment_size >= self._segment_max_bytes:
            self._rotate_before_next_append = True
        return chunk

    def close(self, status: SessionStatus, reason: Optional[str] = None) -> None:
        """Finalize metadata while preserving all payload files unchanged."""
        if self._closed:
            return
        if status == SessionStatus.OPEN:
            raise ValueError("不能以 open 状态关闭会话")
        self._close_segment()
        self._record_event(
            "connection_closed",
            status=status.value,
            reason=reason,
            total_bytes=self._total_bytes,
        )
        self._metadata.update(
            {
                "status": status.value,
                "ended_at": _utc_now(),
                "total_bytes": self._total_bytes,
                "segments": self._segments,
                "sha256": self._hasher.hexdigest(),
            }
        )
        self._save_metadata()
        self._closed = True

    def _open_segment(self) -> None:
        self._segment_number += 1
        self._segment_path = self.session_dir / "payload-{0:06d}.bin".format(self._segment_number)
        self._segment_file = self._segment_path.open("xb")
        self._segment_size = 0
        self._segments.append({"name": self._segment_path.name, "bytes": 0})
        self._record_event("segment_opened", segment=self._segment_path.name)

    def _close_segment(self) -> None:
        if self._segment_file is None:
            return
        self._segment_file.flush()
        os.fsync(self._segment_file.fileno())
        self._segment_file.close()
        self._segment_file = None

    def _record_event(self, name: str, **values: object) -> None:
        self._event_sequence += 1
        event: Dict[str, object] = {
            "sequence": self._event_sequence,
            "time": _utc_now(),
            "event": name,
        }
        event.update(values)
        _append_event(self._events_path, event, self._fsync_policy == "always")

    def _save_metadata(self) -> None:
        _write_json_atomically(self.session_dir / "session.json", self._metadata)


def recover_open_sessions(storage_root: Path) -> List[str]:
    """Mark abandoned open sessions interrupted without changing payload bytes."""
    recovered: List[str] = []
    for metadata_path in Path(storage_root).glob("incoming/*/*/*/*/session.json"):
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            if metadata.get("status") != SessionStatus.OPEN.value:
                continue
            session_dir = metadata_path.parent
            payload_paths = sorted(
                path for path in session_dir.iterdir() if path.is_file() and _PAYLOAD_NAME.fullmatch(path.name)
            )
            digest = hashlib.sha256()
            total_bytes = 0
            segments = []
            for payload_path in payload_paths:
                size = 0
                with payload_path.open("rb") as payload:
                    while True:
                        chunk = payload.read(64 * 1024)
                        if not chunk:
                            break
                        digest.update(chunk)
                        size += len(chunk)
                        total_bytes += len(chunk)
                segments.append({"name": payload_path.name, "bytes": size})

            events_path = session_dir / "events.jsonl"
            event_sequence = _next_event_sequence(events_path)
            _append_event(
                events_path,
                {"sequence": event_sequence, "time": _utc_now(), "event": "recovered"},
                True,
            )
            metadata.update(
                {
                    "status": SessionStatus.INTERRUPTED.value,
                    "ended_at": _utc_now(),
                    "total_bytes": total_bytes,
                    "segments": segments,
                    "sha256": digest.hexdigest(),
                }
            )
            _write_json_atomically(metadata_path, metadata)
            recovered.append(str(metadata["session_id"]))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as error:
            _LOGGER.error("无法恢复会话目录 %s: %s", metadata_path.parent, error)
    return recovered


def _next_event_sequence(events_path: Path) -> int:
    sequence = 0
    if not events_path.exists():
        return 1
    for line in events_path.read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(line)
            sequence = max(sequence, int(event.get("sequence", 0)))
        except (TypeError, ValueError, json.JSONDecodeError):
            continue
    return sequence + 1
