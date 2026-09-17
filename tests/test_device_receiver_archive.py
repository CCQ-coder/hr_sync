"""Behavioral tests for lossless session archiving."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

try:
    from device_raw_receiver.archive import SessionArchive, recover_open_sessions
    from device_raw_receiver.models import SessionStatus
except ImportError as import_error:  # TDD: express missing behavior as a test failure.
    ARCHIVE_IMPORT_ERROR = import_error
    SessionArchive = None
    SessionStatus = None
    recover_open_sessions = None
else:
    ARCHIVE_IMPORT_ERROR = None


class SessionArchiveTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.storage_root = Path(self.temporary_directory.name) / "receiver-data"

    def require_archive_module(self) -> None:
        self.assertIsNone(ARCHIVE_IMPORT_ERROR, f"archive module is unavailable: {ARCHIVE_IMPORT_ERROR}")

    def create_archive(self, segment_max_bytes: int = 64) -> "SessionArchive":
        self.require_archive_module()
        return SessionArchive.create(
            storage_root=self.storage_root,
            local_host="0.0.0.0",
            local_port=9100,
            peer_host="192.168.10.55",
            peer_port=50123,
            segment_max_bytes=segment_max_bytes,
            fsync_policy="always",
        )

    @staticmethod
    def payload_paths(archive: "SessionArchive") -> list[Path]:
        return sorted(archive.session_dir.glob("payload-*.bin"))

    @staticmethod
    def metadata(archive: "SessionArchive") -> dict[str, object]:
        return json.loads((archive.session_dir / "session.json").read_text(encoding="utf-8"))

    def test_preserves_binary_and_gbk_bytes_in_arrival_order(self) -> None:
        archive = self.create_archive()
        expected = b"\x00A" + "中文".encode("gbk") + b"\xff"

        archive.append(b"\x00A")
        archive.append("中文".encode("gbk"))
        archive.append(b"\xff")
        archive.close(SessionStatus.CLOSED)

        actual = b"".join(path.read_bytes() for path in self.payload_paths(archive))
        metadata = self.metadata(archive)
        self.assertEqual(expected, actual)
        self.assertEqual("closed", metadata["status"])
        self.assertEqual(7, metadata["total_bytes"])
        self.assertEqual(hashlib.sha256(expected).hexdigest(), metadata["sha256"])

    def test_rotates_before_next_complete_buffer_without_splitting_bytes(self) -> None:
        archive = self.create_archive(segment_max_bytes=3)

        archive.append(b"abcd")
        archive.append(b"ef")
        archive.close(SessionStatus.CLOSED)

        payloads = self.payload_paths(archive)
        self.assertEqual(["payload-000001.bin", "payload-000002.bin"], [path.name for path in payloads])
        self.assertEqual(b"abcd", payloads[0].read_bytes())
        self.assertEqual(b"ef", payloads[1].read_bytes())
        self.assertEqual(b"abcdef", b"".join(path.read_bytes() for path in payloads))

    def test_records_offsets_without_copying_payload_into_audit_log(self) -> None:
        archive = self.create_archive()
        archive.append(b"secret-raw-bytes")
        archive.close(SessionStatus.CLOSED)

        events_path = archive.session_dir / "events.jsonl"
        events = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines()]
        write_event = next(event for event in events if event["event"] == "data_persisted")
        self.assertEqual(0, write_event["offset"])
        self.assertEqual(16, write_event["length"])
        self.assertNotIn("secret-raw-bytes", events_path.read_text(encoding="utf-8"))


class SessionRecoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.storage_root = Path(self.temporary_directory.name) / "receiver-data"

    def test_marks_open_session_interrupted_without_changing_payload(self) -> None:
        if ARCHIVE_IMPORT_ERROR is not None:
            self.fail(f"archive module is unavailable: {ARCHIVE_IMPORT_ERROR}")
        archive = SessionArchive.create(
            self.storage_root, "0.0.0.0", 9100, "192.168.10.55", 50123, 64, "always"
        )
        self.addCleanup(archive._close_segment)
        archive.append(b"before-crash")
        before = {path.name: path.read_bytes() for path in sorted(archive.session_dir.glob("payload-*.bin"))}

        recovered = recover_open_sessions(self.storage_root)

        after = {path.name: path.read_bytes() for path in sorted(archive.session_dir.glob("payload-*.bin"))}
        metadata = json.loads((archive.session_dir / "session.json").read_text(encoding="utf-8"))
        self.assertEqual([archive.session_id], recovered)
        self.assertEqual(before, after)
        self.assertEqual("interrupted", metadata["status"])
        self.assertEqual(len(b"before-crash"), metadata["total_bytes"])


if __name__ == "__main__":
    unittest.main()
