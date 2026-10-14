"""Regression coverage for Wantongda flying-probe TXT validation."""

import tempfile
import unittest
from pathlib import Path

import flying_probe_sync as sync


def make_text(**overrides):
    values = {
        "Pad_Net_Count": "217 91",
        "Job_Extents": "-383350 50630 -50480 236000",
        "A_Align": "-2123300 226800 -50480 1255350 -50480 1255350",
        "Reference_Net": "1",
        "Pads_Per_Side": "66 151 0",
        "B_Align": "0 0 0 0 0 0 0",
        "Orientation": "1 1 0 0",
        "Panel_Obsolete": "",
        "Panel_Layout": "1 1 1 0 0",
        "Test_Counters": "69 46 23 00:08:34",
        "Want_Ext_Resist_Test": "0 30.00 5.00",
    }
    values.update(overrides)
    return "\n".join(
        key if not values[key] else key + " " + values[key]
        for key in sync.EXPECTED_KEYS
    ) + "\n"


class FlyingProbeParserTests(unittest.TestCase):
    def test_valid_fixed_format_parses_to_typed_values(self):
        parsed = sync.parse_flying_probe_bytes(make_text().encode("utf-8"))

        self.assertEqual("VALID", parsed.validation_status)
        self.assertEqual(217, parsed.values["pad_count"])
        self.assertEqual(91, parsed.values["net_count"])
        self.assertEqual(-383350, parsed.values["job_extent_1"])
        self.assertEqual(1, parsed.values["orientation_1"])
        self.assertEqual(514, parsed.values["test_duration_seconds"])

    def test_huge_duration_is_invalid_and_not_converted_to_bigint_seconds(self):
        parsed = sync.parse_flying_probe_bytes(
            make_text(Test_Counters="7 4 3 5124095576030430:34:08").encode("utf-8")
        )

        self.assertEqual("INVALID", parsed.validation_status)
        self.assertIsNone(parsed.values["test_duration_seconds"])
        self.assertIn("DURATION_EXCEEDS_LIMIT", {issue.code for issue in parsed.issues})

    def test_compact_zero_duration_is_a_supported_legacy_spelling(self):
        parsed = sync.parse_flying_probe_bytes(
            make_text(Test_Counters="1 1 0 0:00").encode("utf-8")
        )

        self.assertEqual("VALID", parsed.validation_status)
        self.assertEqual(0, parsed.values["test_duration_seconds"])

    def test_side_total_mismatch_is_a_warning_not_a_silent_rewrite(self):
        parsed = sync.parse_flying_probe_bytes(
            make_text(Pad_Net_Count="640 129", Pads_Per_Side="320 0 0").encode("utf-8")
        )

        self.assertEqual("WARNING", parsed.validation_status)
        self.assertEqual(640, parsed.values["pad_count"])
        self.assertEqual(320, parsed.values["pads_side_1"])
        self.assertIn("PAD_SIDE_TOTAL_MISMATCH", {issue.code for issue in parsed.issues})

    def test_counter_mismatch_is_an_error(self):
        parsed = sync.parse_flying_probe_bytes(
            make_text(Test_Counters="7 4 2 00:08:34").encode("utf-8")
        )

        self.assertEqual("INVALID", parsed.validation_status)
        self.assertIn("TEST_COUNTER_MISMATCH", {issue.code for issue in parsed.issues})

    def test_non_default_b_alignment_is_preserved_as_warning(self):
        parsed = sync.parse_flying_probe_bytes(
            make_text(B_Align="1 1843070 50490 303700 1249310 303700 1249310").encode("utf-8")
        )

        self.assertEqual("WARNING", parsed.validation_status)
        self.assertEqual(1, parsed.values["b_align_1"])
        self.assertIn("NONDEFAULT_B_ALIGN", {issue.code for issue in parsed.issues})


class FlyingProbeDiscoveryTests(unittest.TestCase):
    def test_scan_keeps_device_identity_and_ignores_unassigned_root_ini(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            device_dir = root / "25-EP-427"
            device_dir.mkdir()
            (device_dir / "p2l000001a.txt").write_text(make_text(), encoding="utf-8")
            (root / "orphan.ini").write_text(make_text(), encoding="utf-8")

            scan = sync.scan_source_directory(root, "customer-b")

        self.assertEqual(1, len(scan.records))
        self.assertEqual("25-EP-427", scan.records[0].device_code)
        self.assertEqual("25-EP-427/p2l000001a.txt", scan.records[0].source_rel_path)
        self.assertEqual(1, len(scan.ignored_files))
        self.assertEqual("orphan.ini", scan.ignored_files[0].source_rel_path)

    def test_unmapped_device_is_invalid_instead_of_creating_a_dynamic_table(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            device_dir = root / "unknown-device"
            device_dir.mkdir()
            (device_dir / "job.txt").write_text(make_text(), encoding="utf-8")

            scan = sync.scan_source_directory(root, "customer-b")

        self.assertEqual("INVALID", scan.records[0].validation_status)
        self.assertIn("UNKNOWN_DEVICE", {issue.code for issue in scan.records[0].parsed.issues})


class FlyingProbeDatabaseBoundaryTests(unittest.TestCase):
    def test_only_approved_device_and_audit_tables_can_be_quoted(self):
        self.assertEqual("`qms_flyprobe_25_ep_427`", sync._safe_table_name("qms_flyprobe_25_ep_427"))
        with self.assertRaises(sync.FlyingProbeSyncError):
            sync._safe_table_name("qms_flyprobe_25_ep_427; DROP TABLE qms_work_order")

    def test_version_key_changes_when_content_changes(self):
        first = sync._source_key("customer-b", "25-EP-427", "25-EP-427/a.txt", "a" * 64)
        second = sync._source_key("customer-b", "25-EP-427", "25-EP-427/a.txt", "b" * 64)
        self.assertNotEqual(first, second)


if __name__ == "__main__":
    unittest.main()
