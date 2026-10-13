"""Regression coverage for the clean, shareable ERP release package."""

from __future__ import annotations

import importlib
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXE_NAME = "QMS-ERP数据同步工具-英文字段版"
EXPECTED_FILES = {
    f"{EXE_NAME}.exe",
    "erp_field_registry.json",
    "erp_field_rename_manifest.json",
    "erp_field_rename_preflight.sql",
    "erp_field_rename_apply.sql",
    "erp_field_rename_verify.sql",
    "erp_field_rename_contract.sql",
    "qms_erp_raw_schema.sql",
    "qms_erp_sync_config.example.json",
}


class ReleasePackageTests(unittest.TestCase):
    def setUp(self):
        self.package = importlib.import_module("prepare_release_package")

    def create_source_tree(self, root: Path) -> Path:
        dist = root / "dist"
        for relative in (
            f"dist/{EXE_NAME}.exe",
            "erp_field_registry.json",
            "outputs/erp_field_rename_manifest.json",
            "sql/erp_field_rename_preflight.sql",
            "sql/erp_field_rename_apply.sql",
            "sql/erp_field_rename_verify.sql",
            "sql/erp_field_rename_contract.sql",
            "qms_erp_raw_schema.sql",
            "qms_erp_sync_config.example.json",
        ):
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(relative, encoding="utf-8")
        return dist

    def test_stages_only_allowlisted_artifacts_and_omits_neighbor_config_and_state(self):
        """A normal packaging run must not ingest unrelated sensitive dist files."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dist = self.create_source_tree(root)
            (dist / "qms_erp_sync_config.json").write_text("secret-not-to-copy", encoding="utf-8")
            (dist / "qms_erp_sync_state.json").write_text("state-not-to-copy", encoding="utf-8")

            release = self.package.stage_release_package(root, dist, EXE_NAME)

            self.assertEqual({path.name for path in release.iterdir()}, EXPECTED_FILES)
            self.assertFalse((release / "qms_erp_sync_config.json").exists())
            self.assertFalse((release / "qms_erp_sync_state.json").exists())
            self.assertEqual((release / "erp_field_registry.json").read_text(encoding="utf-8"),
                             "erp_field_registry.json")

    def test_refuses_existing_release_directory_with_sensitive_or_unexpected_file(self):
        """A polluted release directory must block rather than be cleaned or copied into."""
        for unexpected in ("qms_erp_sync_config.json", "qms_erp_sync_state.json", "notes.txt"):
            with self.subTest(unexpected=unexpected), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                dist = self.create_source_tree(root)
                release = dist / f"{EXE_NAME}-发布包"
                release.mkdir()
                blocked = release / unexpected
                blocked.write_text("must-remain-untouched", encoding="utf-8")

                with self.assertRaisesRegex(self.package.ReleasePackageError, "意外文件"):
                    self.package.stage_release_package(root, dist, EXE_NAME)

                self.assertEqual(blocked.read_text(encoding="utf-8"), "must-remain-untouched")
                self.assertEqual({path.name for path in release.iterdir()}, {unexpected})

    def test_rejects_unsafe_executable_names_before_release_paths_are_constructed(self):
        """A build name must never be able to escape the caller's dist directory."""
        for unsafe in (
            None, 42, "", "..", "../x", "a/b", r"a\b", r"C:\\release", r"\\server\share",
            "a:b", "bad name", "CON",
        ):
            with self.subTest(unsafe=unsafe):
                with self.assertRaisesRegex(self.package.ReleasePackageError, "可执行文件名称"):
                    self.package.release_directory(Path("C:/safe/dist"), unsafe)
        self.assertEqual(self.package.validate_executable_name(EXE_NAME), EXE_NAME)

    def test_checked_in_example_config_is_password_free_and_allowlisted(self):
        """The only shipped configuration is a placeholder-based example template."""
        example = json.loads((ROOT / "qms_erp_sync_config.example.json").read_text(encoding="utf-8"))
        self.assertEqual(example["database_username"], "<填写 QMS 应用账号>")
        self.assertEqual(example["database_password"], "<填写数据库密码>")
        self.assertNotIn("qms_erp_sync_config.json", EXPECTED_FILES)
        self.assertNotIn("qms_erp_sync_state.json", EXPECTED_FILES)

    def test_build_script_validates_then_stages_through_the_release_helper(self):
        """The build boundary must invoke the release allowlist, not copy all of dist."""
        script = (ROOT / "build_exe.ps1").read_text(encoding="utf-8")
        self.assertIn("prepare_release_package.py", script)
        self.assertIn("--validate-only", script)
        self.assertIn("--exe-name", script)


if __name__ == "__main__":
    unittest.main()
