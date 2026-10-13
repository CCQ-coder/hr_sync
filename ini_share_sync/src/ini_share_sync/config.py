"""Read and validate the synchroniser's JSON configuration."""

import json
from pathlib import Path

from .filesystem import read_text


class ConfigError(ValueError):
    """Raised when sync_config.json is missing or unsuitable for a safe run."""


class SyncConfig:
    """Validated paths and device identifier.

    This deliberately uses a plain class instead of :mod:`dataclasses`: Python
    3.4 is the newest CPython runtime that can start on Windows XP.
    """

    def __init__(self, source_root, target_root, device_id):
        self.source_root = source_root
        self.target_root = target_root
        self.device_id = device_id


DEVICE_ID_PLACEHOLDER = "请填写设备编号"


def load_config(config_path: Path) -> SyncConfig:
    """Load a configuration file and reject values that could target another path."""
    try:
        raw = json.loads(read_text(config_path, encoding="utf-8-sig"))
        source_root = Path(raw["source_root"])
        target_root_text = str(raw["target_root"])
        target_root = Path(target_root_text)
        device_id = str(raw["device_id"]).strip()
    except (OSError, KeyError, TypeError, ValueError) as exc:
        raise ConfigError("无法读取有效的 sync_config.json") from exc

    if not str(source_root):
        raise ConfigError("source_root 不能为空")
    unc_segments = [segment for segment in target_root_text[2:].split("\\") if segment]
    if not target_root_text.startswith("\\\\") or len(unc_segments) < 2:
        raise ConfigError("target_root 必须是 UNC 共享目录，例如 \\服务器\\共享目录")
    if (
        not device_id
        or device_id == DEVICE_ID_PLACEHOLDER
        or device_id in (".", "..")
        or any(character in device_id for character in "\\/:\x00")
    ):
        raise ConfigError("device_id 必须是安全的单层目录名")

    return SyncConfig(
        source_root=source_root,
        target_root=target_root,
        device_id=device_id,
    )
