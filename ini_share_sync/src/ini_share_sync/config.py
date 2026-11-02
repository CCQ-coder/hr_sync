"""Read and validate the synchroniser's JSON configuration."""

import json
from pathlib import Path
from urllib.parse import urlsplit

from .filesystem import read_text


class ConfigError(ValueError):
    """Raised when sync_config.json is missing or unsuitable for a safe run."""


class SyncConfig:
    """Validated paths and device identifier.

    This deliberately uses a plain class instead of :mod:`dataclasses`: Python
    3.4 is the newest CPython runtime that can start on Windows XP.
    """

    def __init__(self, source_root, target_root, device_id, server_url=None, upload_token=None, ca_cert=None):
        self.source_root = source_root
        self.target_root = target_root
        self.device_id = device_id
        self.server_url = server_url
        self.upload_token = upload_token
        self.ca_cert = ca_cert


DEVICE_ID_PLACEHOLDER = "请填写设备编号"


def load_config(config_path: Path) -> SyncConfig:
    """Load a configuration file and reject values that could target another path."""
    try:
        raw = json.loads(read_text(config_path, encoding="utf-8-sig"))
        source_root = Path(raw["source_root"])
        cloud = "server_url" in raw
        target_root_text = str(raw.get("target_root", "")) if cloud else str(raw["target_root"])
        target_root = None if cloud else Path(target_root_text)
        server_url = raw.get("server_url")
        upload_token = raw.get("upload_token")
        ca_cert = None
        if cloud:
            if not isinstance(server_url, str) or not server_url or any(character.isspace() for character in server_url):
                raise ValueError("server_url 必须是 HTTPS 地址")
            parsed = urlsplit(server_url)
            if (parsed.scheme != "https" or not parsed.hostname or parsed.username is not None
                    or parsed.password is not None or parsed.query or parsed.fragment):
                raise ValueError("server_url 必须是无凭据的 HTTPS 地址")
            parsed.port  # Validate a supplied port before the scheduled run starts.
            if (not isinstance(upload_token, str) or not upload_token
                    or any(ord(character) < 33 or ord(character) > 126 for character in upload_token)):
                raise ValueError("upload_token 必须是有效设备令牌")
            if not isinstance(raw.get("ca_cert"), str) or not raw["ca_cert"].strip():
                raise ValueError("ca_cert 不能为空")
            ca_cert = Path(raw["ca_cert"])
            if not ca_cert.is_absolute():
                ca_cert = config_path.parent / ca_cert
            if not ca_cert.is_file():
                raise ValueError("ca_cert 文件不存在")
            server_url = server_url.rstrip("/")
        device_id = str(raw["device_id"]).strip()
    except (OSError, KeyError, TypeError, ValueError) as exc:
        raise ConfigError("无法读取有效的 sync_config.json") from exc

    if not str(source_root):
        raise ConfigError("source_root 不能为空")
    unc_segments = [segment for segment in target_root_text[2:].split("\\") if segment]
    if not cloud and (not target_root_text.startswith("\\\\") or len(unc_segments) < 2):
        raise ConfigError("target_root 必须是 UNC 共享目录，例如 \\服务器\\共享目录")
    if (
        not device_id
        or len(device_id) > 160
        or device_id == DEVICE_ID_PLACEHOLDER
        or device_id in (".", "..")
        or device_id.endswith(".")
        or device_id.split(".", 1)[0].upper() in (
            "CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5",
            "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3", "LPT4",
            "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
        )
        or any(ord(character) < 32 or character in '\\/:*?"<>|' for character in device_id)
    ):
        raise ConfigError("device_id 必须是安全的单层目录名")

    return SyncConfig(
        source_root=source_root,
        target_root=target_root,
        device_id=device_id,
        server_url=server_url,
        upload_token=upload_token,
        ca_cert=ca_cert,
    )
