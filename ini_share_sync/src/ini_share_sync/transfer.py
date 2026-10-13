"""Write destination TXT files without exposing incomplete copies."""

import ctypes
import hashlib
import os
import uuid
from pathlib import Path

from .config import SyncConfig
from .discovery import SyncCandidate
from .filesystem import ensure_directory


FILE_WRITE_ATTRIBUTES = 0x0100
FILE_SHARE_READ = 0x0001
FILE_SHARE_WRITE = 0x0002
OPEN_EXISTING = 3
FILE_ATTRIBUTE_NORMAL = 0x0080
WINDOWS_EPOCH_AS_FILETIME = 116444736000000000


class FileTime(ctypes.Structure):
    """The Windows FILETIME structure, kept compatible with Python 3.4."""

    _fields_ = [
        ("dwLowDateTime", ctypes.c_ulong),
        ("dwHighDateTime", ctypes.c_ulong),
    ]


def timestamp_to_filetime(timestamp):
    """Convert a Python epoch timestamp to the 100-nanosecond Windows format."""
    value = int(round(timestamp * 10000000)) + WINDOWS_EPOCH_AS_FILETIME
    return FileTime(value & 0xFFFFFFFF, value >> 32)


def copy_windows_file_times(source_path, destination_path):
    """Apply the source creation and modification times to the published TXT."""
    source_stat = source_path.stat()
    creation_time = timestamp_to_filetime(source_stat.st_ctime)
    modification_time = timestamp_to_filetime(source_stat.st_mtime)
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.CreateFileW(
        str(destination_path),
        FILE_WRITE_ATTRIBUTES,
        FILE_SHARE_READ | FILE_SHARE_WRITE,
        None,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        None,
    )
    invalid_handle = ctypes.c_void_p(-1).value
    if handle == invalid_handle:
        raise ctypes.WinError()
    try:
        if not kernel32.SetFileTime(
            handle,
            ctypes.byref(creation_time),
            None,
            ctypes.byref(modification_time),
        ):
            raise ctypes.WinError()
    finally:
        kernel32.CloseHandle(handle)


def target_path(config: SyncConfig, candidate: SyncCandidate) -> Path:
    """Return the agreed remote TXT location for a source job."""
    return config.target_root / config.device_id / (candidate.job_name + ".txt")


def copy_as_txt(source_path: Path, destination_path: Path) -> str:
    """Copy raw bytes to a temporary target and return the published bytes' hash."""
    ensure_directory(destination_path.parent)
    temporary = destination_path.with_name(
        "." + destination_path.name + "." + uuid.uuid4().hex + ".part"
    )
    try:
        digest = hashlib.sha256()
        with source_path.open("rb") as source_handle, temporary.open("wb") as target_handle:
            for block in iter(lambda: source_handle.read(1024 * 1024), b""):
                target_handle.write(block)
                digest.update(block)
        os.replace(str(temporary), str(destination_path))
        copy_windows_file_times(source_path, destination_path)
        return digest.hexdigest()
    finally:
        if temporary.exists():
            temporary.unlink()
