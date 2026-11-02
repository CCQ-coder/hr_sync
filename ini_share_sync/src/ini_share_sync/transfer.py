"""Write destination TXT files without exposing incomplete copies."""

import base64
import ctypes
import hashlib
from http.client import HTTPSConnection, HTTPException
import json
import os
from pathlib import Path
import ssl
from urllib.parse import urlsplit
import uuid

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


def post_json(config, endpoint, payload):
    """Send one verified HTTPS request; redirects and failures remain retries."""
    parsed = urlsplit(config.server_url)
    if parsed.scheme != "https":
        raise ValueError("server_url 必须使用 HTTPS")
    context = ssl.create_default_context(cafile=str(config.ca_cert))
    connection = HTTPSConnection(parsed.hostname, parsed.port, timeout=30, context=context)
    try:
        connection.request(
            "POST", parsed.path.rstrip("/") + endpoint,
            body=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8", "X-Device-Token": config.upload_token},
        )
        response = connection.getresponse()
        if not 200 <= response.status < 300:
            raise OSError("QMS 上传失败，HTTP " + str(response.status))
    except HTTPException as exc:
        raise OSError("QMS HTTPS 响应无效") from exc
    finally:
        connection.close()


def upload_ini(config, candidate):
    """Upload a bounded, stable raw INI using the legacy TXT timestamp conversion."""
    before = candidate.source_path.stat()
    with candidate.source_path.open("rb") as handle:
        content = handle.read(8 * 1024 * 1024 + 1)
    after = candidate.source_path.stat()
    if len(content) > 8 * 1024 * 1024:
        raise ValueError("INI 超过 8 MiB")
    if (len(content) != before.st_size or
            any(getattr(before, key) != getattr(after, key) for key in ("st_size", "st_ctime", "st_mtime", "st_ino"))):
        raise ValueError("INI 读取期间发生变化，下次重试")
    created = timestamp_to_filetime(after.st_ctime)
    modified = timestamp_to_filetime(after.st_mtime)
    fingerprint = hashlib.sha256(content).hexdigest()
    post_json(config, "/api/v1/flying-probe/device-files", {
        "schemaVersion": 1,
        "deviceId": config.device_id,
        "jobName": candidate.job_name,
        "createdFileTime": (created.dwHighDateTime << 32) | created.dwLowDateTime,
        "modifiedFileTime": (modified.dwHighDateTime << 32) | modified.dwLowDateTime,
        "sha256": fingerprint,
        "contentBase64": base64.b64encode(content).decode("ascii"),
    })
    return fingerprint
