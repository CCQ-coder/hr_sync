"""Later ERP exports win when an older export is overwritten."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pymysql

import qms_erp_sync as sync


class CrossExportOrderTests(unittest.TestCase):
    def test_changed_older_export_replays_later_export(self) -> None:
        class Connection:
            def cursor(self):
                return self

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def commit(self):
                pass

            def rollback(self):
                pass

            def close(self):
                pass

        class Client:
            def __init__(self, _config):
                self.value = None
                self.fail_later = True

            def _connect(self):
                return Connection()

            def _existing_source_tables(self, _cursor):
                return set()

            def _upsert_source_records(self, _cursor, _table, records):
                if self.fail_later and records[-1].row_hash == "newer":
                    self.fail_later = False
                    raise pymysql.OperationalError(2013, "connection lost")
                self.value = records[-1].row_hash

            def _deactivate_removed_file_records(self, _cursor, _removed):
                return 0

        def records(_config, _callback, stats, *, source_directory, selected_files):
            path = selected_files[0]
            stats.files_scanned += 1
            stats.raw_records += 1
            value = path.read_text(encoding="utf-8")
            yield sync.RawSourceRecord(
                source_file=path.as_posix(), sheet_name="Sheet1", source_row_no=2,
                business_key="order-1", source_key="same-business-record", row_hash=value,
                field_values={}, source_table="qms_material", field_definitions={},
            ), None

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            incremental = root / "incremental"
            earlier = incremental / "2026-10-19" / "orders.xls"
            later = incremental / "2026-10-20" / "orders.xls"
            earlier.parent.mkdir(parents=True)
            later.parent.mkdir(parents=True)
            earlier.write_text("old", encoding="utf-8")
            later.write_text("newer", encoding="utf-8")
            config = {"skip_initialization": True, "incremental_directory": str(incremental)}
            _, checkpoints = sync.build_source_scan_plan(config, {})
            checkpoints[sync.SOURCE_IDENTITY_VERSION_STATE_KEY] = "5"

            client = Client(config)
            with patch.object(sync, "state_path", return_value=root / "state.json"), \
                    patch.object(sync, "iter_all_source_records", side_effect=records), \
                    patch.object(sync, "QmsDatabaseClient", return_value=client), \
                    patch.object(sync, "log_line"):
                sync.save_state(checkpoints)
                earlier.write_text("changed-old", encoding="utf-8")
                with self.assertRaises(sync.SyncError):
                    sync.synchronize_database_directory(config, False, lambda _: None)
                progress = sync.load_state()
                self.assertEqual(
                    sync.source_file_checkpoint(earlier),
                    progress[sync.source_file_state_key("incremental", incremental, earlier)],
                )
                self.assertEqual("1", progress.get(sync.BASELINE_REPLAY_STATE_KEY))
                result = sync.synchronize_database_directory(config, False, lambda _: None)

            self.assertEqual(2, result.source_files)
            self.assertEqual("newer", client.value)


if __name__ == "__main__":
    unittest.main()
