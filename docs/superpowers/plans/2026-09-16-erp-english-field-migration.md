# ERP English Field Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace every ERP dynamic Chinese MySQL column with a stable English `erp_` column, retain Chinese Excel headers as MySQL comments, and provide a data-preserving migration SQL package.

**Architecture:** A checked-in field registry is the single authority for the `(target table, source file, sheet, unique Excel header)` to English database-column mapping. The synchronizer carries field definitions alongside field values and creates or verifies `LONGTEXT NULL` fields with their Excel comments. A generator derives an auditable manifest, preflight SQL, rename SQL, verification SQL, mapping JSON/XLSX, and updated BI example SQL from the same registry.

**Tech Stack:** Python 3, PyMySQL, xlrd, openpyxl, unittest, PyInstaller, MySQL 5.7+/8.0-compatible `ALTER TABLE CHANGE COLUMN` SQL.

**Spec:** `docs/superpowers/specs/2026-09-16-erp-english-field-migration-design.md`

## Global Constraints

- All new dynamic database names must match `^erp_[a-z][a-z0-9_]{0,59}$` and be at most 64 UTF-8 bytes.
- Each dynamic field must have `LONGTEXT NULL COMMENT 'Excel列名：<中文列名>'`.
- Chinese headers must never be interpolated into SQL identifiers or comments without validation or bound parameters.
- The normal synchronizer must not rename database fields; only generated migration SQL may rename them.
- Unknown post-release Excel headers must fail with an actionable registry error rather than create a Chinese physical column.
- The repository has no `.git`; do not run commit commands or claim commits.

---

### Task 1: Establish the checked-in field registry and deterministic naming API

**Files:**
- Create: `erp_field_registry.json`
- Create: `generate_erp_field_registry.py`
- Create: `tests/test_erp_field_registry.py`
- Modify: `qms_erp_sync.py:621-660`
- Modify: `generate_field_mapping_data.py:120-165`

**Interfaces:**
- Produces `ErpFieldDefinition(table_name: str, source_file: str, sheet_name: str, excel_source_header: str, excel_unique_header: str, database_column: str, legacy_database_column: str, column_comment: str)`.
- Produces `load_erp_field_registry(path: Path | None = None) -> ErpFieldRegistry`.
- Produces `ErpFieldRegistry.resolve(table_name: str, source_file: str, sheet_name: str, excel_source_header: str, excel_unique_header: str, column_index: int) -> ErpFieldDefinition`.
- Consumed by raw-record construction, work-order construction, mapping export, and migration generation.

- [ ] **Step 1: Write failing registry tests**

```python
def test_registry_resolves_a_readable_english_column_and_chinese_comment():
    registry = sync.load_erp_field_registry(REGISTRY_PATH)
    field = registry.resolve(
        "qms_purchase_order", "采购订单资料.xls.xls", "Test",
        "采购单号", "采购单号", 1,
    )
    assert field.database_column == "erp_purchase_order_no"
    assert field.column_comment == "Excel列名：采购单号"
    assert field.legacy_database_column == "erp_采购单号"


def test_registry_rejects_an_unregistered_header_without_creating_chinese_name():
    registry = sync.load_erp_field_registry(REGISTRY_PATH)
    with pytest.raises(sync.SyncError, match="字段注册表"):
        registry.resolve("qms_purchase_order", "采购订单资料.xls.xls", "Test", "新列", "新列", 99)
```

- [ ] **Step 2: Run the focused test to verify failure**

Run: `D:\project\hr_sync\.venv\Scripts\python.exe -m unittest tests.test_erp_field_registry -v`

Expected: FAIL because the registry API and registry file do not yet exist.

- [ ] **Step 3: Generate and review the registry**

Implement a generator that reads `BI数据源` through the existing header iterator and emits one JSON record per actual `(table, unique header)` field. Use business terminology such as `purchase_order_no`, `processing_method`, `unit_price`, `supplier_name`, `delivery_date`, `quantity`, and explicit `duplicate_N` suffixes. Use `other_N`, `bi_N`, `mc_N`, or `blank_column_N` only for source headings that contain no business meaning. Reject registry entries if their target table is not in `BUSINESS_SOURCE_TABLES ∪ {qms_work_order}` or their English column collides inside a table.

- [ ] **Step 4: Implement registry loading and resolution**

Implement immutable `ErpFieldDefinition` and `ErpFieldRegistry` in `qms_erp_sync.py`. Build a lookup by exact source scope and a second lookup by `(table_name, excel_unique_header)` only when it maps to the same field definition. Derive `legacy_database_column` with a retained `legacy_database_column_name()` function that exactly reproduces pre-migration behavior. Validate the English regex, byte length, duplicate keys, duplicated target database columns, and comments at load time.

- [ ] **Step 5: Run the focused test to verify pass**

Run: `D:\project\hr_sync\.venv\Scripts\python.exe -m unittest tests.test_erp_field_registry -v`

Expected: PASS for English naming, comments, duplicate names, and unknown-header rejection.

- [ ] **Step 6: Refresh the mapping data generator contract**

Change `generate_field_mapping_data.py` to use `ErpFieldRegistry.resolve()` instead of `database_column_name()`. Add fields `英文数据库字段`, `数据库字段注释`, and `旧数据库字段` to each mapping row; make the overview describe `erp_<english_snake_case>`.

### Task 2: Propagate field definitions through synchronization and create comments

**Files:**
- Modify: `qms_erp_sync.py:248-260, 804-846, 1016-1139, 1249-1294`
- Modify: `tests/test_percent_field_names.py`
- Create: `tests/test_erp_column_comments.py`

**Interfaces:**
- `RawSourceRecord.field_definitions: Mapping[str, ErpFieldDefinition]` maps each persisted field to its registry definition.
- `QmsDatabaseClient._ensure_erp_columns(cursor, table_name: str, fields: Mapping[str, ErpFieldDefinition]) -> None` creates and verifies all dynamic columns.
- Work-order payload contains `erpFieldDefinitions: Mapping[str, ErpFieldDefinition]` alongside `erpFields`.

- [ ] **Step 1: Write failing comment and write-path tests**

```python
def test_ensure_erp_columns_adds_a_bound_chinese_comment():
    client, cursor = make_client_and_cursor(existing_columns=set())
    field = definition("qms_customer_order", "erp_processing_method", "加工方式")
    client._ensure_erp_columns(cursor, "qms_customer_order", {field.database_column: field})
    sql, params = cursor.calls[-1]
    assert "ADD COLUMN `erp_processing_method` LONGTEXT NULL COMMENT %s" in sql
    assert params == ("Excel列名：加工方式",)


def test_work_order_upsert_uses_registry_english_field_name():
    payload = {"erpFields": {"erp_processing_method": "压合"},
               "erpFieldDefinitions": {"erp_processing_method": definition("qms_work_order", "erp_processing_method", "加工方式")}}
    assert "`erp_processing_method`" in render_upsert(payload)
    assert "erp_加工方式" not in render_upsert(payload)
```

- [ ] **Step 2: Run focused tests to verify failure**

Run: `D:\project\hr_sync\.venv\Scripts\python.exe -m unittest tests.test_erp_column_comments tests.test_percent_field_names -v`

Expected: FAIL because the old code accepts only a column-name iterable and lacks field-definition metadata.

- [ ] **Step 3: Carry definitions from Excel rows to raw and work-order records**

At the point where `unique_headers()` is paired with row values, resolve a registry definition for every header using table/file/sheet/column context. Store `definition.database_column -> database_cell_value(value)` and `definition.database_column -> definition` together. For production instructions, build both `erpFields` and `erpFieldDefinitions` from the same resolved definitions.

- [ ] **Step 4: Implement comment-safe schema handling**

Replace the old iterable-only `_ensure_erp_columns` with a mapping-based implementation. For missing fields, issue batched `ALTER TABLE` statements where every `COMMENT` is a bound `%s` parameter. For existing fields, read `column_comment` from `information_schema.columns`; issue `MODIFY COLUMN <quoted name> LONGTEXT NULL COMMENT %s` only when the desired comment differs. Invalidate/update the column metadata cache after each schema change. Validate names through an ASCII-only regex before quoting.

- [ ] **Step 5: Update source and work-order UPSERT SQL**

Keep existing parameterized SQL behavior but derive `erp_columns` exclusively from registry-provided English fields. Preserve the current source-record idempotency keys, row hashes, QMS standard mapped columns, and `CURRENT_TIMESTAMP(6)` logic. Remove the percent-in-identifier special case only after the old regression test is replaced by an English-name regression proving values remain parameterized.

- [ ] **Step 6: Run focused tests to verify pass**

Run: `D:\project\hr_sync\.venv\Scripts\python.exe -m unittest tests.test_erp_column_comments tests.test_percent_field_names tests.test_erp_field_registry -v`

Expected: PASS; SQL contains only English ERP identifiers and Chinese comments are bound values.

### Task 3: Generate the audited MySQL rename package and rewrite BI examples

**Files:**
- Create: `generate_erp_field_migration.py`
- Create: `sql/erp_field_rename_preflight.sql`
- Create: `sql/erp_field_rename_apply.sql`
- Create: `sql/erp_field_rename_verify.sql`
- Create: `outputs/erp_field_rename_manifest.json`
- Modify: `bi_dashboard_queries.sql`
- Create: `tests/test_erp_field_migration.py`

**Interfaces:**
- `build_rename_manifest(registry: ErpFieldRegistry) -> list[RenameManifestRow]` emits only fields where old and new names differ.
- `render_preflight_sql(manifest: Sequence[RenameManifestRow]) -> str` lists database/server metadata and expected old/new fields.
- `render_apply_sql(manifest: Sequence[RenameManifestRow]) -> str` emits one `ALTER TABLE ... CHANGE COLUMN` per row.
- `render_verify_sql(manifest: Sequence[RenameManifestRow]) -> str` verifies old names are absent and new names/comments are present.

- [ ] **Step 1: Write failing migration-generator tests**

```python
def test_apply_sql_renames_and_comments_a_longtext_legacy_field():
    row = RenameManifestRow("qms_customer_order", "erp_加工方式", "erp_processing_method", "Excel列名：加工方式")
    sql = render_apply_sql([row])
    assert "CHANGE COLUMN `erp_加工方式` `erp_processing_method` LONGTEXT NULL COMMENT 'Excel列名：加工方式'" in sql


def test_manifest_rejects_two_legacy_columns_mapping_to_one_target_column():
    with pytest.raises(ValueError, match="目标字段冲突"):
        build_rename_manifest(registry_with_collision())
```

- [ ] **Step 2: Run focused tests to verify failure**

Run: `D:\project\hr_sync\.venv\Scripts\python.exe -m unittest tests.test_erp_field_migration -v`

Expected: FAIL because no migration generator exists.

- [ ] **Step 3: Implement manifest and SQL generator**

Generate a JSON manifest containing source scope, table, legacy name, new name, comment, and `LONGTEXT NULL` definition. Write preflight SQL that retrieves server version and every expected old/new column from `information_schema.columns`, escaping the underscore in `erp_`. Write apply SQL with a warning header, a table-by-table ordering, and `CHANGE COLUMN` statements with quoted identifiers and SQL-escaped comments. Write verify SQL that detects remaining old fields, missing new fields, and mismatched comments. Do not make normal synchronization execute this SQL.

- [ ] **Step 4: Rewrite BI example SQL from the manifest**

Parse all backtick-quoted legacy ERP identifiers in `bi_dashboard_queries.sql`. Replace them only when the manifest contains an unambiguous old-to-new mapping across the referenced table. Fail the generator on ambiguous names rather than silently selecting a different business-table mapping.

- [ ] **Step 5: Run focused tests to verify pass and generate artifacts**

Run: `D:\project\hr_sync\.venv\Scripts\python.exe -m unittest tests.test_erp_field_migration -v`

Expected: PASS.

Run: `D:\project\hr_sync\.venv\Scripts\python.exe generate_erp_field_migration.py`

Expected: creates the manifest and all three SQL files with no Chinese dynamic identifier in newly generated SQL targets.

### Task 4: Refresh user-facing mapping, documentation, packaging, and full verification

**Files:**
- Modify: `README.md`
- Modify: `generate_field_mapping_workbook.mjs`
- Modify: `build_exe.ps1`
- Modify: `qms_erp_raw_schema.sql`
- Regenerate: `outputs/excel_database_field_mapping_data.json`
- Regenerate: `outputs/ERP_Excel_数据库字段对照表-实体字段版.xlsx`
- Regenerate: `dist/QMS-ERP数据同步工具-英文字段版.exe`
- Copy: `sql/erp_field_rename_*.sql` and `outputs/erp_field_rename_manifest.json` into `dist/`

**Interfaces:**
- User receives the English-field EXE, JSON mapping/manifest, and three reviewed SQL files in `dist/`.

- [ ] **Step 1: Write/update delivery-level test assertions**

```python
def test_generated_mapping_rows_use_english_erp_fields_and_chinese_comments():
    mapping = json.loads((ROOT / "outputs/excel_database_field_mapping_data.json").read_text(encoding="utf-8"))
    row = next(item for item in mapping["mapping_rows"] if item["Excel 原始列名"] == "加工方式")
    assert re.fullmatch(r"erp_[a-z][a-z0-9_]{0,59}", row["英文数据库字段"])
    assert row["数据库字段注释"].startswith("Excel列名：")
```

- [ ] **Step 2: Run delivery assertion to verify failure before regeneration**

Run: `D:\project\hr_sync\.venv\Scripts\python.exe -m unittest tests.test_erp_field_migration -v`

Expected: FAIL until the mapping generator and registry are wired together.

- [ ] **Step 3: Update documentation and schema hints**

Document the new registry, Chinese MySQL comments, required backup/preflight/apply/verify order, and the rule for future Excel headers. Update the schema hint and mapping workbook labels to state `erp_<english_snake_case>` rather than `erp_<Excel列名>`.

- [ ] **Step 4: Regenerate mapping artifacts and package executable**

Run the mapping JSON generator, the provided workbook generator, and `build_exe.ps1` after copying migration assets into the packaged distribution directory. Do not overwrite legacy EXEs; name the new executable `QMS-ERP数据同步工具-英文字段版.exe`.

- [ ] **Step 5: Run full verification**

Run: `D:\project\hr_sync\.venv\Scripts\python.exe -m unittest discover -s tests -v`

Expected: all tests PASS.

Run: `D:\project\hr_sync\.venv\Scripts\python.exe -m py_compile qms_erp_sync.py generate_field_mapping_data.py generate_erp_field_migration.py`

Expected: exit code 0.

Run: `Get-Item 'dist\\QMS-ERP数据同步工具-英文字段版.exe', 'dist\\erp_field_rename_preflight.sql', 'dist\\erp_field_rename_apply.sql', 'dist\\erp_field_rename_verify.sql', 'dist\\erp_field_rename_manifest.json'`

Expected: all five deliverables exist.

- [ ] **Step 6: Record the verification outcome**

Report the number of renamed field mappings, affected tables, package path, and the required SQL execution order. Do not state that the production database has been changed because the generated SQL is deliberately not executed by this task.
