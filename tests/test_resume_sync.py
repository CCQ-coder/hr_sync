"""Recovery and overwritten-file behavior for the ERP directory synchronizer."""

import os
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pymysql

import qms_erp_sync as sync


class FileCheckpointTests(unittest.TestCase):
    def test_same_size_and_mtime_overwrite_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workbook = root / "2026-10-20" / "采购订单资料.xls"
            workbook.parent.mkdir()
            workbook.write_bytes(b"first")
            original_stat = workbook.stat()
            config = {"skip_initialization": True, "incremental_directory": str(root)}
            _, previous = sync.build_source_scan_plan(config, {})
            original_fingerprint = sync.directory_fingerprint(root)

            workbook.write_bytes(b"other")
            os.utime(workbook, ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns))

            groups, _ = sync.build_source_scan_plan(config, previous)
            self.assertEqual([workbook], list(groups[0].files))
            self.assertNotEqual(original_fingerprint, sync.directory_fingerprint(root))

    def test_interrupted_baseline_replay_keeps_incremental_files_pending(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            baseline = root / "baseline"
            incremental = root / "incremental"
            baseline.mkdir()
            incremental.mkdir()
            (baseline / "base.xls").write_bytes(b"base")
            (incremental / "delta.xls").write_bytes(b"delta")
            config = {
                "initialization_directory": str(baseline),
                "incremental_directory": str(incremental),
            }
            _, previous = sync.build_source_scan_plan(config, {})
            previous[sync.BASELINE_REPLAY_STATE_KEY] = "1"
            groups, _ = sync.build_source_scan_plan(config, previous)
            self.assertEqual(["incremental"], [group.role for group in groups])

    def test_removed_rows_are_scoped_to_the_overwritten_file(self) -> None:
        first_key = "source-file:incremental:2026-10-20/one.xls"
        second_key = "source-file:incremental:2026-10-20/two.xls"
        state = {
            sync.file_membership_state_key(first_key): json.dumps({
                "raw": {"qms_material": ["old", "shared"]},
                "work_orders": ["ERP-EXCEL:old", "ERP-EXCEL:shared"],
                "batches": ["old-batch", "shared-batch"],
            }),
            sync.file_membership_state_key(second_key): json.dumps({
                "raw": {"qms_material": ["shared"]},
                "work_orders": ["ERP-EXCEL:shared"],
                "batches": ["shared-batch"],
            }),
        }
        current = {"raw": {"qms_material": []}, "work_orders": [], "batches": []}
        self.assertEqual({
            "raw": {"qms_material": ["old"]},
            "work_orders": ["ERP-EXCEL:old"],
            "batches": ["old-batch"],
        }, sync.removed_file_membership(state, first_key, current))

    def test_deactivation_sql_limits_changes_to_owned_keys_and_erp_orders(self) -> None:
        class Cursor:
            rowcount = 1

            def __init__(self):
                self.calls = []

            def execute(self, statement, parameters):
                self.calls.append((statement, parameters))

        client = object.__new__(sync.QmsDatabaseClient)
        client.tenant = "customer-b"
        cursor = Cursor()
        count = client._deactivate_removed_file_records(cursor, {
            "raw": {"qms_material": ["old"]},
            "work_orders": ["ERP-EXCEL:old"],
            "batches": ["old-batch"],
        })
        self.assertEqual(3, count)
        self.assertEqual(3, len(cursor.calls))
        self.assertIn("`tenant_code` = %s", cursor.calls[0][0])
        self.assertEqual(("customer-b", "old"), cursor.calls[0][1])
        self.assertIn("`source_system` = 'ERP_EXCEL'", cursor.calls[1][0])
        self.assertIn("work_order.`source_system` = 'ERP_EXCEL'", cursor.calls[2][0])

    def test_source_table_creation_is_not_repeated_for_every_batch(self) -> None:
        class Cursor:
            def __init__(self):
                self.statements = []

            def execute(self, statement, _parameters=None):
                self.statements.append(statement)

        client = object.__new__(sync.QmsDatabaseClient)
        client._legacy_json_checked = set()
        client._source_table_ready = set()
        cursor = Cursor()
        with patch.object(client, "_read_table_columns", return_value={}), \
                patch.object(client, "_ensure_erp_columns"):
            client._ensure_source_table_schema(cursor, "qms_material", {})
            client._ensure_source_table_schema(cursor, "qms_material", {})
        create_statements = [item for item in cursor.statements if "CREATE TABLE" in item]
        self.assertEqual(1, len(create_statements))


class ResumeTests(unittest.TestCase):
    def test_file_replaced_while_reading_does_not_advance_checkpoint(self) -> None:
        class FakeConnection:
            rollbacks = 0

            def cursor(self):
                return self

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def commit(self):
                raise AssertionError("changed source must not commit")

            def rollback(self):
                self.rollbacks += 1

            def close(self):
                pass

        class FakeClient:
            def __init__(self, connection):
                self.connection = connection

            def _connect(self):
                return self.connection

            def _upsert_source_records(self, *_args):
                pass

        def fake_records(_config, _callback, stats, *, source_directory, selected_files):
            path = selected_files[0]
            stats.files_scanned += 1
            stats.raw_records += 1
            path.write_bytes(b"later")
            yield sync.RawSourceRecord(
                source_file=path.name, sheet_name="Sheet1", source_row_no=2,
                business_key="1", source_key="raw1", row_hash="hash1",
                field_values={}, source_table="qms_material", field_definitions={},
            ), None

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            source.mkdir()
            (source / "today.xls").write_bytes(b"first")
            config = {"skip_initialization": True, "incremental_directory": str(source)}
            connection = FakeConnection()
            with patch.object(sync, "state_path", return_value=root / "state.json"), \
                    patch.object(sync, "iter_all_source_records", side_effect=fake_records), \
                    patch.object(sync, "QmsDatabaseClient", return_value=FakeClient(connection)):
                with self.assertRaisesRegex(sync.SyncError, "覆盖"):
                    sync.synchronize_database_directory(config, False, lambda _: None)
                self.assertEqual({}, sync.load_state())
            self.assertEqual(1, connection.rollbacks)

    def test_overwrite_deactivates_rows_removed_from_the_same_file(self) -> None:
        class FakeConnection:
            def cursor(self):
                return self

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def commit(self):
                pass

            def close(self):
                pass

        class FakeClient:
            def __init__(self):
                self.removed = []

            def _connect(self):
                return FakeConnection()

            def _upsert_source_records(self, *_args):
                pass

            def _upsert_work_order(self, *_args):
                return "work-order-id"

            def _upsert_batch(self, *_args):
                pass

            def _deactivate_removed_file_records(self, _cursor, removed):
                self.removed.append(removed)
                return sum(map(len, removed["raw"].values())) + len(removed["work_orders"]) + len(removed["batches"])

        def fake_records(_config, _callback, stats, *, source_directory, selected_files):
            path = selected_files[0]
            stats.files_scanned += 1
            for number in (1, 2) if path.read_bytes() == b"first" else (1,):
                stats.raw_records += 1
                stats.work_order_records += 1
                yield sync.RawSourceRecord(
                    source_file=path.name, sheet_name="Sheet1", source_row_no=number + 1,
                    business_key=str(number), source_key=f"raw{number}", row_hash=f"hash{number}",
                    field_values={}, source_table="qms_material", field_definitions={},
                ), {"sourceKey": f"ERP-EXCEL:{number}", "workOrderNo": str(number), "batchNo": f"B{number}"}

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            source.mkdir()
            workbook = source / "today.xls"
            workbook.write_bytes(b"first")
            config = {"skip_initialization": True, "incremental_directory": str(source)}
            client = FakeClient()
            with patch.object(sync, "state_path", return_value=root / "state.json"), \
                    patch.object(sync, "iter_all_source_records", side_effect=fake_records), \
                    patch.object(sync, "QmsDatabaseClient", return_value=client):
                sync.synchronize_database_directory(config, False, lambda _: None)
                workbook.write_bytes(b"later")
                result = sync.synchronize_database_directory(config, False, lambda _: None)
            self.assertEqual(3, result.deactivated)
            self.assertEqual({
                "raw": {"qms_material": ["raw2"]},
                "work_orders": ["ERP-EXCEL:2"],
                "batches": ["B2"],
            }, client.removed[-1])

    def test_disconnect_preserves_first_file_and_retries_only_second(self) -> None:
        class FakeConnection:
            def __init__(self):
                self.commits = 0
                self.rollbacks = 0

            def cursor(self):
                return self

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def commit(self):
                self.commits += 1

            def rollback(self):
                self.rollbacks += 1

            def close(self):
                pass

        class FakeClient:
            def __init__(self, _config):
                self.connections = []
                self.fail_second = True

            def _connect(self):
                connection = FakeConnection()
                self.connections.append(connection)
                return connection

            def _upsert_source_records(self, _cursor, _table, records):
                if self.fail_second and any(record.source_file == "second.xls" for record in records):
                    raise pymysql.OperationalError(2013, "connection lost")

            def _deactivate_removed_file_records(self, _cursor, _removed):
                return 0

        def fake_records(_config, _callback, stats, *, source_directory, selected_files):
            for path in selected_files:
                stats.files_scanned += 1
                stats.raw_records += 1
                name = path.name
                yield sync.RawSourceRecord(
                    source_file=name, sheet_name="Sheet1", source_row_no=2,
                    business_key=name, source_key=name, row_hash=name,
                    field_values={}, source_table="qms_material",
                    field_definitions={},
                ), None

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            source.mkdir()
            (source / "first.xls").write_bytes(b"first")
            (source / "second.xls").write_bytes(b"second")
            config = {"skip_initialization": True, "incremental_directory": str(source)}
            first_client = FakeClient(config)
            with patch.object(sync, "state_path", return_value=root / "state.json"), \
                    patch.object(sync, "iter_all_source_records", side_effect=fake_records), \
                    patch.object(sync, "QmsDatabaseClient", return_value=first_client):
                with self.assertRaises(sync.SyncError):
                    sync.synchronize_database_directory(config, False, lambda _: None)
                first_state = sync.load_state()
                first_key = sync.source_file_state_key("incremental", source, source / "first.xls")
                second_key = sync.source_file_state_key("incremental", source, source / "second.xls")
                self.assertIn(first_key, first_state)
                self.assertNotIn(second_key, first_state)
                self.assertEqual(1, first_client.connections[0].commits)
                self.assertEqual(1, first_client.connections[1].rollbacks)

                retry_client = FakeClient(config)
                retry_client.fail_second = False
                with patch.object(sync, "QmsDatabaseClient", return_value=retry_client):
                    result = sync.synchronize_database_directory(config, False, lambda _: None)
                self.assertEqual(1, result.source_files)
                self.assertEqual(1, len(retry_client.connections))
                self.assertIn(second_key, sync.load_state())


if __name__ == "__main__":
    unittest.main()
