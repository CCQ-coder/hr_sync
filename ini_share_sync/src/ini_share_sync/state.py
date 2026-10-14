"""Fingerprint source files and persist only successful sync results."""

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path

from .discovery import SyncCandidate
from .filesystem import ensure_directory, read_text, write_text


def sha256_file(path):
    """Return a stable content fingerprint without decoding the INI file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def candidate_key(candidate):
    """Build a case-insensitive state key from the complete source path."""
    return str(candidate.source_path.resolve()).casefold()


def load_state(path):
    """Load last-successful fingerprints, returning an empty state on first run."""
    if not path.exists():
        return {}

    raw = json.loads(read_text(path, encoding="utf-8"))
    files = raw.get("files") if isinstance(raw, dict) else None
    if not isinstance(files, dict):
        raise ValueError("sync_state.json 格式无效")

    entries = {}
    migrated_legacy_entries = False
    legacy_timestamp = datetime.fromtimestamp(path.stat().st_mtime).replace(
        microsecond=0
    ).isoformat()
    for key, value in files.items():
        if isinstance(value, str):
            if len(value) != 64 or any(character not in "0123456789abcdef" for character in value.casefold()):
                raise ValueError("sync_state.json 旧版文件记录格式无效")
            entries[str(key)] = {
                "sha256": value,
                "synced_at": legacy_timestamp,
            }
            migrated_legacy_entries = True
            continue
        if not isinstance(value, dict):
            raise ValueError("sync_state.json 文件记录格式无效")
        fingerprint = value.get("sha256")
        synced_at = value.get("synced_at")
        if not isinstance(fingerprint, str) or not isinstance(synced_at, str):
            raise ValueError("sync_state.json 文件记录缺少 sha256 或 synced_at")
        entries[str(key)] = {"sha256": fingerprint, "synced_at": synced_at}

    if migrated_legacy_entries:
        save_state(path, entries)
    return entries


def save_state(path, entries):
    """Atomically replace the state file after a source file is copied."""
    ensure_directory(path.parent)
    temporary = path.with_name("." + path.name + "." + str(os.getpid()) + ".tmp")
    try:
        write_text(
            temporary,
            json.dumps({"files": entries}, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        os.replace(str(temporary), str(path))
    finally:
        if temporary.exists():
            temporary.unlink()
