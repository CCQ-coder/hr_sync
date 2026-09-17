"""Executable-boundary tests for the Windows raw receiver package."""

from __future__ import annotations

import json
import io
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

try:
    from device_raw_receiver.main import run
except ImportError as import_error:  # TDD: an absent CLI is an assertion failure.
    MAIN_IMPORT_ERROR = import_error
    run = None
else:
    MAIN_IMPORT_ERROR = None


ROOT = Path(__file__).resolve().parents[1]


class ReceiverCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.package_directory = Path(self.temporary_directory.name) / "package"
        self.package_directory.mkdir()

    def require_main_module(self) -> None:
        self.assertIsNone(MAIN_IMPORT_ERROR, f"CLI module is unavailable: {MAIN_IMPORT_ERROR}")

    def write_package_inputs(self) -> None:
        (self.package_directory / "DeviceRawReceiver.exe").write_bytes(b"placeholder")
        (self.package_directory / "device_receiver_config.json").write_text(
            json.dumps({"tcp_port": 9100, "allowed_networks": ["192.168.10.0/24"]}), encoding="utf-8"
        )

    def run_powershell_script(self, name: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(ROOT / name),
                "-PackageDirectory",
                str(self.package_directory),
                "-WhatIf",
            ],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            errors="replace",
        )

    def test_missing_config_returns_usage_error_without_starting_listener(self) -> None:
        self.require_main_module()

        stderr = io.StringIO()
        with redirect_stderr(stderr):
            result = run(["--config", str(self.package_directory / "missing.json")])
        self.assertEqual(2, result)
        self.assertIn("配置错误", stderr.getvalue())

    def test_installer_whatif_validates_package_without_creating_task(self) -> None:
        self.require_main_module()
        self.write_package_inputs()

        result = self.run_powershell_script("install_device_raw_receiver_task.ps1")

        self.assertEqual(0, result.returncode, result.stderr)

    def test_remover_whatif_does_not_require_an_existing_task(self) -> None:
        self.require_main_module()

        result = self.run_powershell_script("remove_device_raw_receiver_task.ps1")

        self.assertEqual(0, result.returncode, result.stderr)


if __name__ == "__main__":
    unittest.main()
