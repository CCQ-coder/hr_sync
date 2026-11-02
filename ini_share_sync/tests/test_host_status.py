import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from ini_share_sync.host_status import capture_host_status, write_host_status


class HostStatusTests(unittest.TestCase):
    @unittest.skipUnless(sys.platform == "win32", "Windows counters are required")
    def test_capture_has_v1_fields_and_valid_ranges(self):
        sample = capture_host_status("FEIZHEN-01")

        self.assertEqual(
            {
                "schemaVersion", "deviceId", "sampledAt", "cpuPercent",
                "memoryTotalBytes", "memoryAvailableBytes", "systemDiskTotalBytes",
                "systemDiskFreeBytes", "uptimeSeconds",
            },
            set(sample),
        )
        self.assertEqual(1, sample["schemaVersion"])
        self.assertEqual("FEIZHEN-01", sample["deviceId"])
        self.assertTrue(sample["sampledAt"].endswith("+00:00"))
        if sample["cpuPercent"] is not None:
            self.assertGreaterEqual(sample["cpuPercent"], 0)
            self.assertLessEqual(sample["cpuPercent"], 100)
        self.assertGreater(sample["memoryTotalBytes"], 0)
        self.assertLessEqual(sample["memoryAvailableBytes"], sample["memoryTotalBytes"])
        self.assertGreater(sample["systemDiskTotalBytes"], 0)
        self.assertLessEqual(sample["systemDiskFreeBytes"], sample["systemDiskTotalBytes"])
        self.assertGreaterEqual(sample["uptimeSeconds"], 0)

    @unittest.skipUnless(sys.platform == "win32", "Windows task entry point is required")
    def test_status_mode_uses_configured_device_id_without_source_root(self):
        from ini_share_sync.config import SyncConfig
        from ini_share_sync.main import main

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = SyncConfig(root / "missing-source", root / "share", "FEIZHEN-02")
            with patch("ini_share_sync.main.load_config", return_value=config):
                self.assertEqual(0, main(["--status-only", "--config", str(root / "config.json")]))

            path = root / "share" / "FEIZHEN-02" / "host-status.json"
            self.assertTrue(path.is_file())
            self.assertEqual("FEIZHEN-02", json.loads(path.read_text(encoding="utf-8"))["deviceId"])
            self.assertFalse((root / "sync_state.json").exists())

    def test_failed_replace_preserves_previous_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old = {"deviceId": "FEIZHEN-01", "sampledAt": "old"}
            new = {"deviceId": "FEIZHEN-01", "sampledAt": "new"}
            path = write_host_status(root, "FEIZHEN-01", old)

            with patch("ini_share_sync.host_status.os.replace", side_effect=OSError("blocked")):
                with self.assertRaises(OSError):
                    write_host_status(root, "FEIZHEN-01", new)

            self.assertEqual(old, json.loads(path.read_text(encoding="utf-8")))
            self.assertEqual(["host-status.json"], sorted(p.name for p in path.parent.iterdir()))
