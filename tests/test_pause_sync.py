"""Pausing a normal sync leaves committed files resumable."""

import queue
import tempfile
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import qms_erp_sync as sync


class PauseSyncTests(unittest.TestCase):
    def test_pause_requested_during_final_file_keeps_auto_monitor_suspended(self):
        events = queue.Queue()
        summary = sync.SyncSummary("daily", 1, 1, 0, 0, 0, False)
        events.put(("done", (summary, False, "fingerprint")))
        pause_event = threading.Event()
        pause_event.set()
        logs = []
        statuses = []
        app = SimpleNamespace(
            events=events, pause_event=pause_event, _monitor_paused=True,
            _record_successful_snapshot=lambda _: None, _write_log=logs.append,
            status_var=SimpleNamespace(set=statuses.append),
            _set_running=lambda _: None, after=lambda *_args: None,
            _drain_events=lambda: None,
        )
        with patch.object(sync.messagebox, "showinfo") as showinfo:
            sync.SyncApplication._drain_events(app)
        self.assertTrue(app._monitor_paused)
        self.assertIn("手动同步完成", logs[-1])
        self.assertEqual(logs[-1], statuses[-1])
        showinfo.assert_not_called()

    def test_pause_button_requests_stop_and_suspends_auto_monitor(self):
        self.assertTrue(hasattr(sync.SyncApplication, "_request_pause"))
        messages = []
        states = []
        pause_event = threading.Event()
        app = SimpleNamespace(
            running=True, pause_event=pause_event, _monitor_paused=False,
            pause_button=SimpleNamespace(configure=lambda **state: states.append(state)),
            status_var=SimpleNamespace(set=messages.append), _write_log=messages.append,
        )
        sync.SyncApplication._request_pause(app)
        self.assertTrue(pause_event.is_set())
        self.assertTrue(app._monitor_paused)
        self.assertEqual({"state": "disabled"}, states[-1])
        self.assertIn("当前文件", messages[-1])

    def test_pause_after_current_file_keeps_checkpoint_and_resumes_next_file(self):
        commits = []
        scanned = []

        class Connection:
            def cursor(self):
                return self

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def commit(self):
                commits.append("commit")

            def rollback(self):
                commits.append("rollback")

            def close(self):
                pass

        class Client:
            def _connect(self):
                return Connection()

            def _upsert_source_records(self, *_args, **_kwargs):
                pass

            def _deactivate_removed_file_records(self, *_args):
                return 0

        def records(_config, _callback, stats, *, selected_files, **_kwargs):
            path = selected_files[0]
            scanned.append(path.name)
            stats.files_scanned += 1
            stats.raw_records += 1
            yield sync.RawSourceRecord(
                source_file=path.as_posix(), sheet_name="Test", source_row_no=2,
                business_key=path.stem, source_key=f"ERP5:{path.stem}",
                row_hash=path.stem, field_values={},
                source_table="qms_purchase_order", field_definitions={},
            ), None

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            daily = root / "daily"
            first = daily / "2026-10-26" / "采购订单资料.xls"
            second = daily / "2026-10-27" / "采购订单资料.xls"
            for path in (first, second):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(path.parent.name.encode())
            pause_event = threading.Event()
            config = {"skip_initialization": True, "incremental_directory": str(daily)}

            def callback(message):
                if message.startswith("已提交并保存断点："):
                    pause_event.set()

            with patch.object(sync, "state_path", return_value=root / "state.json"), \
                    patch.object(sync, "iter_all_source_records", side_effect=records), \
                    patch.object(sync, "QmsDatabaseClient", return_value=Client()):
                sync.save_state({sync.SOURCE_IDENTITY_VERSION_STATE_KEY: "5"})
                with self.assertRaisesRegex(sync.SyncPaused, "已暂停"):
                    sync.synchronize_database_directory(
                        config, False, callback, pause_event=pause_event,
                    )
                self.assertEqual(["采购订单资料.xls"], scanned)
                self.assertEqual(["commit"], commits)
                self.assertEqual(sync.source_file_checkpoint(first), sync.load_state()[
                    sync.source_file_state_key("incremental", daily, first)
                ])
                pause_event.clear()
                sync.synchronize_database_directory(
                    config, False, lambda _: None, pause_event=pause_event,
                )
                self.assertEqual(["采购订单资料.xls"] * 2, scanned)
                self.assertEqual(["commit", "commit"], commits)


if __name__ == "__main__":
    unittest.main()
