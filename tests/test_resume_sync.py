"""Recovery and overwritten-file behavior for the ERP directory synchronizer."""

import os
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pymysql
from openpyxl import Workbook

import qms_erp_sync as sync


class FileCheckpointTests(unittest.TestCase):
    def test_same_named_exports_in_different_daily_roots_have_distinct_identity(self) -> None:
        class Registry:
            def canonical_headers_for(self, _source_file, headers):
                return headers

            def resolve_sheet(self, *_args):
                return []

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            files = []
            for day, order in (("10-19", "A"), ("10-20", "B")):
                folder = root / day
                folder.mkdir()
                path = folder / "客户订单资料.xlsx"
                workbook = Workbook()
                workbook.active.append(["客户订单号"])
                workbook.active.append([order])
                workbook.save(path)
                files.append((folder, path))

            config = {"source_file_keyword": "生产指示资料"}
            with patch.object(sync, "load_erp_field_registry", return_value=Registry()):
                rows = [
                    next(iter(sync.iter_all_source_records(
                        config, lambda _: None, sync.SourceScanStats(),
                        source_directory=folder, selected_files=(path,),
                    )))[0]
                    for folder, path in files
                ]
            self.assertNotEqual(rows[0].source_key, rows[1].source_key)
            self.assertNotEqual(rows[0].source_file, rows[1].source_file)

            first_config = {"skip_initialization": True, "incremental_directory": str(files[0][0])}
            second_config = {"skip_initialization": True, "incremental_directory": str(files[1][0])}
            _, previous = sync.build_source_scan_plan(first_config, {})
            groups, _ = sync.build_source_scan_plan(second_config, previous)
            self.assertEqual([files[1][1]], list(groups[0].files))

    def test_same_path_overwrite_changes_content_key_and_hash(self) -> None:
        class Registry:
            def canonical_headers_for(self, _source_file, headers):
                return headers

            def resolve_sheet(self, *_args):
                return []

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "客户订单资料.xlsx"

            def write_order(order):
                workbook = Workbook()
                workbook.active.append(["客户订单号"])
                workbook.active.append([order])
                workbook.save(path)

            def scan():
                with patch.object(sync, "load_erp_field_registry", return_value=Registry()):
                    return next(iter(sync.iter_all_source_records(
                        {}, lambda _: None, sync.SourceScanStats(),
                        source_directory=root, selected_files=(path,),
                    )))[0]

            write_order("A")
            before = scan()
            write_order("B")
            after = scan()
            self.assertNotEqual(before.source_key, after.source_key)
            self.assertNotEqual(before.row_hash, after.row_hash)

    def test_same_record_in_two_exports_uses_one_source_key(self) -> None:
        class Registry:
            def canonical_headers_for(self, _source_file, headers):
                return headers

            def resolve_sheet(self, *_args):
                return []

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            paths = []
            for day in ("10-19", "10-20"):
                folder = root / day
                folder.mkdir()
                path = folder / "客户订单资料.xlsx"
                workbook = Workbook()
                workbook.active.append(["客户订单号"])
                workbook.active.append(["A"])
                workbook.save(path)
                paths.append(path)
            with patch.object(sync, "load_erp_field_registry", return_value=Registry()):
                keys = [
                    next(iter(sync.iter_all_source_records(
                        {}, lambda _: None, sync.SourceScanStats(),
                        source_directory=root, selected_files=(path,),
                    )))[0].source_key
                    for path in paths
                ]
            self.assertEqual(keys[0], keys[1])

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
        self.assertIn("'SUPERSEDED'", cursor.calls[0][0])
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

    def test_same_legacy_row_is_reused_without_duplicating_the_import(self) -> None:
        raw = sync.RawSourceRecord(
            source_file="D:/daily/客户订单资料.XLS", sheet_name="Test",
            source_row_no=2, business_key="A#行2", source_key="new-key",
            row_hash="same-hash", field_values={},
            source_table="qms_customer_order", field_definitions={},
        )
        old_key = sync.legacy_source_key("客户订单资料.XLS", "Test", 2)
        existing = {old_key: ("客户订单资料.XLS", "same-hash")}

        self.assertEqual(
            old_key,
            sync.compatible_source_key(raw, "客户订单资料.XLS", existing),
        )

    def test_changed_legacy_row_is_preserved_when_new_day_uses_same_row(self) -> None:
        raw = sync.RawSourceRecord(
            source_file="D:/daily/客户订单资料.XLS", sheet_name="Test",
            source_row_no=2, business_key="B#行2", source_key="new-key",
            row_hash="new-hash", field_values={},
            source_table="qms_customer_order", field_definitions={},
        )
        old_key = sync.legacy_source_key("客户订单资料.XLS", "Test", 2)
        existing = {old_key: ("客户订单资料.XLS", "old-hash")}

        self.assertEqual("new-key", sync.compatible_source_key(raw, "客户订单资料.XLS", existing))

    def test_adopted_legacy_row_updates_in_place_after_same_path_overwrite(self) -> None:
        raw = sync.RawSourceRecord(
            source_file="D:/daily/客户订单资料.XLS", sheet_name="Test",
            source_row_no=2, business_key="B#行2", source_key="new-key",
            row_hash="new-hash", field_values={},
            source_table="qms_customer_order", field_definitions={},
        )
        old_key = sync.legacy_source_key("客户订单资料.XLS", "Test", 2)
        self.assertEqual(old_key, sync.compatible_source_key(
            raw, "客户订单资料.XLS", {old_key: (raw.source_file, "old-hash")},
        ))
        self.assertEqual("new-key", sync.compatible_source_key(
            raw, "客户订单资料.XLS", {old_key: ("D:/other/客户订单资料.XLS", "new-hash")},
        ))

    def test_existing_new_key_takes_precedence_over_matching_legacy_row(self) -> None:
        raw = sync.RawSourceRecord(
            source_file="D:/daily/客户订单资料.XLS", sheet_name="Test",
            source_row_no=2, business_key="B#行2", source_key="new-key",
            row_hash="new-hash", field_values={},
            source_table="qms_customer_order", field_definitions={},
        )
        old_key = sync.legacy_source_key("客户订单资料.XLS", "Test", 2)
        existing = {old_key: ("客户订单资料.XLS", "new-hash"), "new-key": (raw.source_file, "new-hash")}
        self.assertEqual("new-key", sync.compatible_source_key(raw, "客户订单资料.XLS", existing))

    def test_legacy_lookup_is_limited_to_tenant_and_current_file(self) -> None:
        class Cursor:
            def __init__(self):
                self.calls = []

            def execute(self, statement, parameters):
                self.calls.append((statement, parameters))

            def fetchall(self):
                return [("old-key", "客户订单资料.XLS", "same-hash")]

        client = object.__new__(sync.QmsDatabaseClient)
        client.tenant = "customer-b"
        cursor = Cursor()
        result = client._source_records_for_file(
            cursor, "qms_customer_order", "客户订单资料.XLS", "D:/daily/客户订单资料.XLS",
        )
        self.assertEqual({"old-key": ("客户订单资料.XLS", "same-hash")}, result)
        self.assertIn("tenant_code = %s", cursor.calls[0][0])
        self.assertIn("source_file IN (%s, %s)", cursor.calls[0][0])
        self.assertEqual(("customer-b", "客户订单资料.XLS", "D:/daily/客户订单资料.XLS"), cursor.calls[0][1])


class CustomerOrderLatestTests(unittest.TestCase):
    class Cursor:
        rowcount = 1

        def __init__(self, rows):
            self.rows = rows
            self.calls = []

        def execute(self, statement, parameters):
            self.calls.append((statement, parameters))

        def fetchall(self):
            return self.rows

    def reconcile(self, rows):
        client = object.__new__(sync.QmsDatabaseClient)
        client.tenant = "customer-b"
        cursor = self.Cursor(rows)
        with patch.object(client, "_read_table_columns", return_value={
            "id": "", "tenant_code": "", "source_key": "", "source_file": "",
            "sheet_name": "", "source_row_no": "", "business_key": "", "row_hash": "",
            "status": "", "created_at": "", "updated_at": "",
            "erp_order_no": "", "erp_internal_product_no": "", "erp_delivery_date": "",
            "erp_order_placed_quantity": "", "erp_tax_inclusive_amount": "",
        }):
            changed = client._reconcile_customer_order_latest(cursor)
        return changed, cursor.calls

    def test_same_order_and_material_updates_original_row_in_place(self) -> None:
        changed, calls = self.reconcile([
            ("original-id", "old-key", "D:/10-19/客户订单资料.XLS", 23255, "ACTIVE", "PI10102490", "L1PT44162A01", "2026-10-19 09:00:00"),
            ("new-id", "new-key", "D:/2026-10-20/客户订单资料.XLS", 3, "ACTIVE", "PI10102490", "L1PT44162A01", "2026-10-20 10:00:00"),
            ("other-material-id", "other-key", "D:/2026-10-20/客户订单资料.XLS", 4, "ACTIVE", "PI10102490", "OTHER", "2026-10-20 10:00:00"),
        ])
        self.assertEqual(1, changed)
        self.assertTrue(any("JOIN `qms_customer_order`" in sql and "`erp_tax_inclusive_amount`" in sql
                            and args[0] == "new-id" and args[2] == "original-id" for sql, args in calls))
        self.assertTrue(any(sql.lstrip().startswith("DELETE") and args[-1] == "new-id"
                            for sql, args in calls))
        self.assertTrue(any(sql.lstrip().startswith("UPDATE") and "`source_key` = %s" in sql
                            and args == ("new-key", "ACTIVE", "customer-b", "original-id")
                            for sql, args in calls))
        self.assertFalse(any("other-material-id" in args for _, args in calls))

    def test_same_file_rows_with_different_delivery_and_quantity_are_merged(self) -> None:
        changed, calls = self.reconcile([
            ("first-id", "first-key", "D:/2026-10-20/客户订单资料.XLS", 79, "ACTIVE", "PI10102533", "04PO43210A01", "2026-10-20 10:00:00"),
            ("second-id", "second-key", "D:/2026-10-20/客户订单资料.XLS", 80, "ACTIVE", "PI10102533", "04PO43210A01", "2026-10-20 10:00:00"),
        ])
        self.assertEqual(1, changed)
        self.assertTrue(any("JOIN `qms_customer_order`" in sql and args[0] == "second-id"
                            for sql, args in calls))
        self.assertTrue(any(sql.lstrip().startswith("DELETE") and args[-1] == "second-id"
                            for sql, args in calls))

    def test_export_date_beats_later_import_time(self) -> None:
        changed, calls = self.reconcile([
            ("old-id", "old-key", "D:/10-19/客户订单资料.XLS", 23255, "ACTIVE", "PI10102490", "L1PT44162A01", "2026-10-21 12:00:00"),
            ("new-id", "new-key", "D:/2026-10-20/客户订单资料.XLS", 3, "ACTIVE", "PI10102490", "L1PT44162A01", "2026-10-20 10:00:00"),
        ])
        self.assertEqual(1, changed)
        self.assertTrue(any(sql.lstrip().startswith("DELETE") and args[-1] == "old-id"
                            for sql, args in calls))

    def test_lone_superseded_row_becomes_active(self) -> None:
        changed, calls = self.reconcile([
            ("old-id", "old-key", "D:/10-19/客户订单资料.XLS", 23255, "SUPERSEDED", "PI10102490", "L1PT44162A01", "2026-10-19 09:00:00"),
        ])
        self.assertEqual(1, changed)
        self.assertEqual(("old-key", "ACTIVE", "customer-b", "old-id"), calls[-1][1])


class ResumeTests(unittest.TestCase):
    def test_unchanged_files_reconcile_existing_customer_order_rows_once(self) -> None:
        class Connection:
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

        class Client:
            calls = 0

            def _connect(self):
                return Connection()

            def _existing_source_tables(self, _cursor):
                return {"qms_customer_order"}

            def _reconcile_customer_order_latest(self, _cursor):
                self.calls += 1
                return 1

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            source.mkdir()
            (source / "客户订单资料.xls").write_bytes(b"already-imported")
            config = {"initialization_directory": str(source), "incremental_directory": "", "skip_initialization": False}
            _, state = sync.build_source_scan_plan(config, {})
            state[sync.SOURCE_IDENTITY_VERSION_STATE_KEY] = "3"
            state[sync.CUSTOMER_ORDER_RECONCILE_STATE_KEY] = "1"
            client = Client()
            with patch.object(sync, "state_path", return_value=root / "state.json"), \
                    patch.object(sync, "QmsDatabaseClient", return_value=client):
                sync.save_state(state)
                self.assertEqual(0, sync.synchronize_database_directory(config, False, lambda _: None).source_files)
                self.assertEqual(1, client.calls)
                self.assertEqual("2", sync.load_state()[sync.CUSTOMER_ORDER_RECONCILE_STATE_KEY])
                sync.synchronize_database_directory(config, False, lambda _: None)
                self.assertEqual(1, client.calls)

    def test_file_sync_does_not_reuse_a_legacy_location_key(self) -> None:
        class Connection:
            def cursor(self):
                return self

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def commit(self):
                if client.reconciled != 1:
                    raise AssertionError("customer orders must reconcile before file commit")

            def close(self):
                pass

        class Client:
            def __init__(self):
                self.written_keys = []
                self.reconciled = 0

            def _connect(self):
                return Connection()

            def _existing_source_tables(self, _cursor):
                return {"qms_customer_order"}

            def _source_records_for_file(self, _cursor, _table, relative, _absolute):
                raise AssertionError("location-based legacy key must not be reused")

            def _upsert_source_records(self, _cursor, _table, records):
                self.written_keys.extend(record.source_key for record in records)

            def _deactivate_removed_file_records(self, _cursor, _removed):
                return 0

            def _reconcile_customer_order_latest(self, _cursor):
                self.reconciled += 1
                return 0

        def fake_records(_config, _callback, stats, *, source_directory, selected_files):
            stats.files_scanned += 1
            stats.raw_records += 1
            yield sync.RawSourceRecord(
                source_file=selected_files[0].resolve().as_posix(), sheet_name="Test",
                source_row_no=2, business_key="A#行2", source_key="new-key",
                row_hash="same-hash", field_values={},
                source_table="qms_customer_order", field_definitions={},
            ), None

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            source.mkdir()
            (source / "客户订单资料.xls").write_bytes(b"today")
            client = Client()
            config = {"skip_initialization": True, "incremental_directory": str(source)}
            messages = []
            with patch.object(sync, "state_path", return_value=root / "state.json"), \
                    patch.object(sync, "iter_all_source_records", side_effect=fake_records), \
                    patch.object(sync, "QmsDatabaseClient", return_value=client):
                sync.synchronize_database_directory(config, False, messages.append)
                self.assertEqual(["new-key"], client.written_keys)
                self.assertEqual(1, client.reconciled)
                state = sync.load_state()
                self.assertEqual("same-hash", state["raw:new-key"])

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

            def _existing_source_tables(self, _cursor):
                return set()

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

            def _existing_source_tables(self, _cursor):
                return set()

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

            def _existing_source_tables(self, _cursor):
                return set()

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
