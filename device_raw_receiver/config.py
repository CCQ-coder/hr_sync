"""Configuration loading and validation for the raw TCP receiver."""

from __future__ import annotations

import ipaddress
import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, Union

Network = Union[ipaddress.IPv4Network, ipaddress.IPv6Network]


class ConfigError(ValueError):
    """Raised when a receiver configuration is unsafe or malformed."""


@dataclass(frozen=True)
class ReceiverConfig:
    """Validated values used to create one TCP receiver instance."""

    listen_host: str
    tcp_port: int
    storage_root: Path
    allowed_networks: Tuple[Network, ...]
    segment_max_bytes: int = 64 * 1024 * 1024
    read_buffer_bytes: int = 64 * 1024
    idle_timeout_seconds: int = 0
    fsync_policy: str = "always"
    max_connections: int = 16
    minimum_free_bytes: int = 1024 * 1024 * 1024

    def allows(self, address: str) -> bool:
        """Return whether a peer address belongs to an approved network."""
        try:
            peer_address = ipaddress.ip_address(address)
        except ValueError:
            return False
        return any(peer_address in network for network in self.allowed_networks)


_REQUIRED_KEYS = (
    "listen_host",
    "tcp_port",
    "storage_root",
    "allowed_networks",
    "segment_max_bytes",
    "read_buffer_bytes",
    "idle_timeout_seconds",
    "fsync_policy",
    "max_connections",
    "minimum_free_bytes",
)


def load_config(path: Path) -> ReceiverConfig:
    """Load a complete receiver JSON configuration from *path*."""
    source_path = Path(path)
    try:
        raw = json.loads(source_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ConfigError("无法读取有效的 JSON 配置文件: {0}".format(source_path)) from error

    if not isinstance(raw, dict):
        raise ConfigError("配置文件根节点必须是对象")
    missing = [key for key in _REQUIRED_KEYS if key not in raw]
    if missing:
        raise ConfigError("配置缺少必填项: {0}".format(", ".join(missing)))

    listen_host = _parse_listen_host(raw["listen_host"])
    tcp_port = _positive_int(raw["tcp_port"], "tcp_port", maximum=65535)
    storage_root = _storage_root(raw["storage_root"])
    allowed_networks = _allowed_networks(raw["allowed_networks"])
    segment_max_bytes = _positive_int(raw["segment_max_bytes"], "segment_max_bytes")
    read_buffer_bytes = _positive_int(raw["read_buffer_bytes"], "read_buffer_bytes")
    idle_timeout_seconds = _non_negative_int(raw["idle_timeout_seconds"], "idle_timeout_seconds")
    max_connections = _positive_int(raw["max_connections"], "max_connections")
    minimum_free_bytes = _non_negative_int(raw["minimum_free_bytes"], "minimum_free_bytes")

    fsync_policy = raw["fsync_policy"]
    if fsync_policy not in ("always", "on_close"):
        raise ConfigError("fsync_policy 只能是 always 或 on_close")

    return ReceiverConfig(
        listen_host=listen_host,
        tcp_port=tcp_port,
        storage_root=storage_root,
        allowed_networks=allowed_networks,
        segment_max_bytes=segment_max_bytes,
        read_buffer_bytes=read_buffer_bytes,
        idle_timeout_seconds=idle_timeout_seconds,
        fsync_policy=fsync_policy,
        max_connections=max_connections,
        minimum_free_bytes=minimum_free_bytes,
    )


def _parse_listen_host(value: object) -> str:
    if not isinstance(value, str):
        raise ConfigError("listen_host 必须是 IP 地址字符串")
    try:
        return str(ipaddress.ip_address(value))
    except ValueError as error:
        raise ConfigError("listen_host 必须是有效 IP 地址") from error


def _positive_int(value: object, name: str, maximum: int = None) -> int:
    if type(value) is not int or value < 1 or (maximum is not None and value > maximum):
        if maximum is None:
            raise ConfigError("{0} 必须是正整数".format(name))
        raise ConfigError("{0} 必须在 1 到 {1} 之间".format(name, maximum))
    return value


def _non_negative_int(value: object, name: str) -> int:
    if type(value) is not int or value < 0:
        raise ConfigError("{0} 必须是非负整数".format(name))
    return value


def _storage_root(value: object) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ConfigError("storage_root 必须是非空路径")
    try:
        storage_root = Path(value).expanduser().resolve()
        temporary_root = Path(tempfile.gettempdir()).resolve()
        storage_root.relative_to(temporary_root)
    except ValueError:
        return storage_root
    except OSError as error:
        raise ConfigError("storage_root 无法解析") from error
    raise ConfigError("storage_root 不能位于系统临时目录")


def _allowed_networks(value: object) -> Tuple[Network, ...]:
    if not isinstance(value, list) or not value:
        raise ConfigError("allowed_networks 必须是非空 CIDR 数组")
    networks = []
    for item in value:
        if not isinstance(item, str):
            raise ConfigError("allowed_networks 必须只包含 CIDR 字符串")
        try:
            networks.append(ipaddress.ip_network(item, strict=False))
        except ValueError as error:
            raise ConfigError("allowed_networks 包含无效 CIDR: {0}".format(item)) from error
    return tuple(networks)
