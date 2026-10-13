"""Behavioral tests for the raw TCP receiver configuration boundary."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

try:
    from device_raw_receiver.config import ConfigError, load_config
except ImportError as import_error:  # TDD: keep the first run an assertion failure.
    CONFIG_IMPORT_ERROR = import_error
    ConfigError = ValueError
    load_config = None
else:
    CONFIG_IMPORT_ERROR = None


class ReceiverConfigurationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.config_directory = Path(self.temporary_directory.name)
        self.storage_root = Path.cwd() / "device_receiver_test_data"

    def valid_config(self, **overrides: object) -> dict[str, object]:
        config: dict[str, object] = {
            "listen_host": "0.0.0.0",
            "tcp_port": 9100,
            "storage_root": str(self.storage_root),
            "allowed_networks": ["192.168.10.0/24"],
            "segment_max_bytes": 16,
            "read_buffer_bytes": 8,
            "idle_timeout_seconds": 0,
            "fsync_policy": "always",
            "max_connections": 2,
            "minimum_free_bytes": 0,
        }
        config.update(overrides)
        return config

    def write_config(self, config: dict[str, object]) -> Path:
        path = self.config_directory / "receiver.json"
        path.write_text(json.dumps(config), encoding="utf-8")
        return path

    def require_config_module(self) -> None:
        self.assertIsNone(CONFIG_IMPORT_ERROR, f"configuration module is unavailable: {CONFIG_IMPORT_ERROR}")

    def test_loads_explicit_tcp_listener_and_matches_cidr(self) -> None:
        self.require_config_module()
        config = load_config(self.write_config(self.valid_config()))

        self.assertEqual("0.0.0.0", config.listen_host)
        self.assertEqual(9100, config.tcp_port)
        self.assertTrue(config.allows("192.168.10.55"))
        self.assertFalse(config.allows("192.168.11.55"))

    def test_rejects_empty_source_whitelist(self) -> None:
        self.require_config_module()

        with self.assertRaisesRegex(ConfigError, "allowed_networks"):
            load_config(self.write_config(self.valid_config(allowed_networks=[])))

    def test_rejects_invalid_listener_boundaries(self) -> None:
        self.require_config_module()

        invalid_values = (
            {"tcp_port": 0},
            {"tcp_port": 65536},
            {"allowed_networks": ["not-a-network"]},
            {"allowed_networks": [], "listen_host": "0.0.0.0"},
            {"segment_max_bytes": 0},
            {"read_buffer_bytes": 0},
            {"idle_timeout_seconds": -1},
            {"fsync_policy": "eventually"},
            {"max_connections": 0},
        )
        for override in invalid_values:
            with self.subTest(override=override), self.assertRaises(ConfigError):
                load_config(self.write_config(self.valid_config(**override)))

    def test_rejects_storage_root_inside_system_temp_directory(self) -> None:
        self.require_config_module()

        with self.assertRaisesRegex(ConfigError, "storage_root"):
            load_config(self.write_config(self.valid_config(storage_root=str(self.config_directory / "payloads"))))


if __name__ == "__main__":
    unittest.main()
