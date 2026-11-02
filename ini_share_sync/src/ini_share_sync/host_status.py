"""Sample this Windows computer and publish one device-specific status file."""

import ctypes
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import time
import uuid

from .filesystem import ensure_directory


class FileTime(ctypes.Structure):
    _fields_ = [("low", ctypes.c_ulong), ("high", ctypes.c_ulong)]


class MemoryStatus(ctypes.Structure):
    _fields_ = [
        ("length", ctypes.c_ulong),
        ("memory_load", ctypes.c_ulong),
        ("total_physical", ctypes.c_ulonglong),
        ("available_physical", ctypes.c_ulonglong),
        ("total_page_file", ctypes.c_ulonglong),
        ("available_page_file", ctypes.c_ulonglong),
        ("total_virtual", ctypes.c_ulonglong),
        ("available_virtual", ctypes.c_ulonglong),
        ("available_extended_virtual", ctypes.c_ulonglong),
    ]


def _filetime_value(value):
    return (value.high << 32) | value.low


def _cpu_times(kernel32):
    idle, kernel, user = FileTime(), FileTime(), FileTime()
    if not kernel32.GetSystemTimes(ctypes.byref(idle), ctypes.byref(kernel), ctypes.byref(user)):
        raise ctypes.WinError()
    return (_filetime_value(idle), _filetime_value(kernel), _filetime_value(user))


def _cpu_percent(before, after):
    idle = after[0] - before[0]
    total = after[1] - before[1] + after[2] - before[2]
    if idle < 0 or total <= 0 or idle > total:
        return None
    return round(100.0 * (total - idle) / total, 2)


def capture_host_status(device_id):
    """Return a QMS-compatible v1 sample using APIs available on Windows XP."""
    kernel32 = ctypes.windll.kernel32
    before = _cpu_times(kernel32)
    time.sleep(0.15)
    cpu_percent = _cpu_percent(before, _cpu_times(kernel32))

    memory = MemoryStatus()
    memory.length = ctypes.sizeof(MemoryStatus)
    if not kernel32.GlobalMemoryStatusEx(ctypes.byref(memory)):
        raise ctypes.WinError()

    system_root = os.path.splitdrive(os.environ.get("SystemRoot", r"C:\WINDOWS"))[0] + "\\"
    available, total, free = ctypes.c_ulonglong(), ctypes.c_ulonglong(), ctypes.c_ulonglong()
    if not kernel32.GetDiskFreeSpaceExW(
        system_root, ctypes.byref(available), ctypes.byref(total), ctypes.byref(free)
    ):
        raise ctypes.WinError()

    try:
        kernel32.GetTickCount64.restype = ctypes.c_ulonglong
        uptime_seconds = kernel32.GetTickCount64() // 1000
    except AttributeError:
        # shortcut: XP's 32-bit counter wraps after 49.7 days; upgrade when XP is retired.
        kernel32.GetTickCount.restype = ctypes.c_ulong
        uptime_seconds = kernel32.GetTickCount() // 1000

    return {
        "schemaVersion": 1,
        "deviceId": device_id,
        "sampledAt": datetime.now(timezone.utc).isoformat(),
        "cpuPercent": cpu_percent,
        "memoryTotalBytes": memory.total_physical,
        "memoryAvailableBytes": memory.available_physical,
        "systemDiskTotalBytes": total.value,
        "systemDiskFreeBytes": free.value,
        "uptimeSeconds": uptime_seconds,
    }


def write_host_status(target_root, device_id, sample):
    """Replace the latest snapshot atomically, leaving the old one on failure."""
    path = Path(target_root) / device_id / "host-status.json"
    ensure_directory(path.parent)
    temporary = path.with_name("." + path.name + "." + uuid.uuid4().hex + ".part")
    try:
        with open(str(temporary), "wb") as handle:
            handle.write(json.dumps(sample, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
        os.replace(str(temporary), str(path))
        return path
    finally:
        if temporary.exists():
            temporary.unlink()
