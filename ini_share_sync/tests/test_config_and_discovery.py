import json
from pathlib import Path
import tempfile
import unittest

from ini_share_sync.config import ConfigError, load_config
from ini_share_sync.discovery import find_candidates


class ConfigAndDiscoveryTests(unittest.TestCase):
    def test_load_config_reads_paths_and_device_id(self):
        """A valid configuration must preserve the supplied root paths and device id."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sync_config.json"
            path.write_text(
                json.dumps(
                    {
                        "source_root": r"D:\WTD\JOBS",
                        "target_root": r"\\Scbgx\数字化\飞针机",
                        "device_id": "FEIZHEN-01",
                    }
                ),
                encoding="utf-8",
            )

            config = load_config(path)

        self.assertEqual(Path(r"D:\WTD\JOBS"), config.source_root)
        self.assertEqual(Path(r"\\Scbgx\数字化\飞针机"), config.target_root)
        self.assertEqual("FEIZHEN-01", config.device_id)

    def test_load_config_rejects_device_id_that_can_escape_target_directory(self):
        """Removing device-id validation would allow writes outside its target folder."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sync_config.json"
            path.write_text(
                json.dumps(
                    {
                        "source_root": r"D:\WTD\JOBS",
                        "target_root": r"\\Scbgx\数字化\飞针机",
                        "device_id": r"..\other-device",
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaises(ConfigError):
                load_config(path)

    def test_rejects_windows_reserved_device_id(self):
        """Windows device names and forbidden suffixes must not alias other folders."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sync_config.json"
            for device_id in ("CON", "aux", "NUL.txt", "LPT1", "FEIZHEN.", "FEIZHEN?", "FEIZHEN<1", "X" * 161):
                with self.subTest(device_id=device_id):
                    path.write_text(
                        json.dumps({
                            "source_root": r"D:\WTD\JOBS",
                            "target_root": r"\\Scbgx\数字化\飞针机",
                            "device_id": device_id,
                        }),
                        encoding="utf-8",
                    )
                    with self.assertRaises(ConfigError):
                        load_config(path)

            path.write_text(
                json.dumps({
                    "source_root": r"D:\WTD\JOBS",
                    "target_root": r"\\Scbgx\数字化\飞针机",
                    "device_id": " FEIZHEN-01 ",
                }),
                encoding="utf-8",
            )
            self.assertEqual("FEIZHEN-01", load_config(path).device_id)

    def test_load_config_rejects_local_target_directory(self):
        """Accepting a local target could silently write data outside the LAN share."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sync_config.json"
            path.write_text(
                json.dumps(
                    {
                        "source_root": r"D:\WTD\JOBS",
                        "target_root": r"D:\not-a-share",
                        "device_id": "FEIZHEN-01",
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaises(ConfigError):
                load_config(path)

    def test_load_config_rejects_unconfigured_device_id_placeholder(self):
        """The shipped placeholder must not create a real remote device folder."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sync_config.json"
            path.write_text(
                json.dumps(
                    {
                        "source_root": r"D:\WTD\JOBS",
                        "target_root": r"\\Scbgx\数字化\飞针机",
                        "device_id": "请填写设备编号",
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaises(ConfigError):
                load_config(path)

    def test_find_candidates_only_returns_first_level_same_name_ini_files(self):
        """Recursing or accepting a differently named INI would sync unintended files."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            valid = root / "p2l046433a"
            valid.mkdir()
            (valid / "p2l046433a.INI").write_bytes(b"valid")
            invalid = root / "different-name"
            invalid.mkdir()
            (invalid / "other.ini").write_bytes(b"ignore")
            nested = valid / "nested"
            nested.mkdir()
            (nested / "nested.ini").write_bytes(b"ignore")

            candidates = find_candidates(root)

        self.assertEqual(["p2l046433a"], [item.job_name for item in candidates])
        self.assertEqual("p2l046433a.INI", candidates[0].source_path.name)
