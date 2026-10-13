from pathlib import Path
import json
import os
import tempfile
import time
import unittest

from ini_share_sync.config import SyncConfig
from ini_share_sync.discovery import SyncCandidate
from ini_share_sync.state import candidate_key, load_state, save_state, sha256_file
from ini_share_sync.transfer import copy_as_txt, target_path


class StateAndTransferTests(unittest.TestCase):
    def test_load_state_migrates_legacy_hash_only_entries(self):
        """Rejecting a prior hash-only state would stop every upgraded scheduled run."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "job.ini"
            source.write_bytes(b"legacy-content")
            candidate = SyncCandidate("job", source)
            state_path = root / "sync_state.json"
            legacy_hash = sha256_file(source)
            state_path.write_text(
                json.dumps({"files": {candidate_key(candidate): legacy_hash}}),
                encoding="utf-8",
            )

            state = load_state(state_path)
            persisted = json.loads(state_path.read_text(encoding="utf-8"))

        entry = state[candidate_key(candidate)]
        self.assertEqual(legacy_hash, entry["sha256"])
        self.assertTrue(entry["synced_at"])
        self.assertEqual(entry, persisted["files"][candidate_key(candidate)])

    def test_state_remembers_last_successful_hash_after_source_changes(self):
        """Without the stored hash, unchanged jobs would be copied every five minutes."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "job.ini"
            source.write_bytes(b"first")
            candidate = SyncCandidate("job", source)
            first_hash = sha256_file(source)
            state_path = root / "sync_state.json"
            first_entry = {
                "sha256": first_hash,
                "synced_at": "2026-09-15T09:30:00",
            }

            save_state(state_path, {candidate_key(candidate): first_entry})
            source.write_bytes(b"changed")
            state = load_state(state_path)

            changed_hash = sha256_file(source)

        state_entry = state[candidate_key(candidate)]
        self.assertEqual(first_entry, state_entry)
        self.assertNotEqual(first_hash, changed_hash)

    def test_copy_as_txt_preserves_all_source_bytes_and_publishes_no_part_file(self):
        """Changing file bytes or leaving a part file would break downstream processing."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "p2l.ini"
            payload = "[job]\r\nvalue=中文\r\n".encode("utf-8")
            source.write_bytes(payload)
            config = SyncConfig(root, root / "share", "FEIZHEN-01")
            destination = target_path(config, SyncCandidate("p2l", source))

            copied_hash = copy_as_txt(source, destination)

            copied = destination.read_bytes()
            destination_hash = sha256_file(destination)
            part_files = list(destination.parent.glob("*.part"))

        self.assertEqual(payload, copied)
        self.assertEqual(destination_hash, copied_hash)
        self.assertEqual("p2l.txt", destination.name)
        self.assertEqual([], part_files)

    def test_copy_as_txt_preserves_source_creation_and_modification_times(self):
        """A remote TXT must retain the source INI's Windows creation and write times."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "job.ini"
            source.write_bytes(b"time-sensitive")
            source_created_at = source.stat().st_ctime
            source_modified_at = time.time() - 3600
            os.utime(str(source), (source_modified_at, source_modified_at))
            time.sleep(1.2)

            destination = root / "share" / "job.txt"
            copy_as_txt(source, destination)
            destination_stat = destination.stat()

        self.assertAlmostEqual(source_created_at, destination_stat.st_ctime, delta=0.25)
        self.assertAlmostEqual(source_modified_at, destination_stat.st_mtime, delta=0.25)
