-- CONTRACT: DESTRUCTIVE separate DBA step, only AFTER verification is clean
-- MySQL 5.7+/8.0. Select the intended database before running this file.
-- Use a UTF-8 client. STOP synchronization and take a verified BACKUP first.
-- DDL auto-commits; this is not a transaction or an idempotent rerun script.
SET @erp_migration_saved_sql_mode = @@SESSION.sql_mode;
SET SESSION sql_mode = CONCAT_WS(',', NULLIF(@@SESSION.sql_mode, ''), 'NO_BACKSLASH_ESCAPES');
SET NAMES utf8mb4;

-- Keep sync stopped. Confirm backup, equal per-tenant scoped counts, zero
-- value mismatches, zero outside-scope targets and zero unassigned legacy values.
-- Confirm BI/other consumers use English fields. Do not run automatically with apply.
ALTER TABLE `qms_material_issue` DROP COLUMN `erp_单价`;
ALTER TABLE `qms_material_issue` DROP COLUMN `erp_单位`;
ALTER TABLE `qms_material_issue` DROP COLUMN `erp_厂内编号`;
ALTER TABLE `qms_material_issue` DROP COLUMN `erp_客户料号`;
ALTER TABLE `qms_material_issue` DROP COLUMN `erp_客户编号`;
ALTER TABLE `qms_material_issue` DROP COLUMN `erp_币别`;
ALTER TABLE `qms_material_issue` DROP COLUMN `erp_输入日期`;
ALTER TABLE `qms_material_issue` DROP COLUMN `erp_输入者`;

SET SESSION sql_mode = @erp_migration_saved_sql_mode;
