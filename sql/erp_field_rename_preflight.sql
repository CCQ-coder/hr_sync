-- PREFLIGHT: inspect every result before approving apply
-- MySQL 5.7+/8.0. Select the intended database before running this file.
-- Use a UTF-8 client. STOP synchronization and take a verified BACKUP first.
-- DDL auto-commits; this is not a transaction or an idempotent rerun script.
SET @erp_migration_saved_sql_mode = @@SESSION.sql_mode;
SET SESSION sql_mode = CONCAT_WS(',', NULLIF(@@SESSION.sql_mode, ''), 'NO_BACKSLASH_ESCAPES');
SET NAMES utf8mb4;

SELECT VERSION() AS mysql_version, DATABASE() AS selected_database, @erp_migration_saved_sql_mode AS original_sql_mode, @@SESSION.sql_mode AS effective_sql_mode;
SELECT TABLE_NAME, COLUMN_NAME, ORDINAL_POSITION, COLUMN_TYPE, IS_NULLABLE,
       COLUMN_DEFAULT, EXTRA, COLUMN_COMMENT, CHARACTER_SET_NAME, COLLATION_NAME, GENERATION_EXPRESSION
FROM information_schema.columns
WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME IN ('qms_customer_order', 'qms_customer_part', 'qms_delivery_note', 'qms_engineering_data', 'qms_finished_goods_receipt', 'qms_material', 'qms_material_issue', 'qms_material_receipt', 'qms_process_output_summary', 'qms_purchase_order', 'qms_work_order')
  AND LEFT(COLUMN_NAME, 4) = 'erp_'
ORDER BY TABLE_NAME, ORDINAL_POSITION;

-- All following issue rows must be resolved. Manually modified definitions,
-- collations/character sets, defaults, indexes and dependencies need DBA review.
SELECT m.*, CASE WHEN o.COLUMN_NAME IS NULL THEN 'missing_old_column'
 WHEN n.COLUMN_NAME IS NOT NULL THEN 'target_already_exists'
 ELSE 'unexpected_definition' END AS issue
FROM (
SELECT 'qms_customer_order' AS table_name, 'erp_下单数量' AS old_field, 'erp_order_placed_quantity' AS new_field, 'Excel列名：下单数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_下单日期' AS old_field, 'erp_order_placed_date' AS new_field, 'Excel列名：下单日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_不含税单价' AS old_field, 'erp_tax_exclusive_unit_price' AS new_field, 'Excel列名：不含税单价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_不含税金额' AS old_field, 'erp_tax_exclusive_amount' AS new_field, 'Excel列名：不含税金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_不含税金额(本位币)' AS old_field, 'erp_tax_exclusive_amount_local_currency' AS new_field, 'Excel列名：不含税金额(本位币)' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_业务员' AS old_field, 'erp_salesperson' AS new_field, 'Excel列名：业务员' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_业务员(客户)' AS old_field, 'erp_salesperson_customer' AS new_field, 'Excel列名：业务员(客户)' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_业务回复人' AS old_field, 'erp_sales_reply_person' AS new_field, 'Excel列名：业务回复人' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_业务回复意见' AS old_field, 'erp_sales_reply_feedback' AS new_field, 'Excel列名：业务回复意见' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_业务回复时间' AS old_field, 'erp_sales_reply_time' AS new_field, 'Excel列名：业务回复时间' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_业务组别名称' AS old_field, 'erp_sales_group_name' AS new_field, 'Excel列名：业务组别名称' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_交期' AS old_field, 'erp_delivery_date' AS new_field, 'Excel列名：交期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_交货地址' AS old_field, 'erp_delivery_address' AS new_field, 'Excel列名：交货地址' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_付款方式' AS old_field, 'erp_payment_method' AS new_field, 'Excel列名：付款方式' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_停止交货' AS old_field, 'erp_stop_delivery' AS new_field, 'Excel列名：停止交货' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_停止投料' AS old_field, 'erp_stop_material_input' AS new_field, 'Excel列名：停止投料' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_其它费' AS old_field, 'erp_other_fee' AS new_field, 'Excel列名：其它费' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_加工工艺' AS old_field, 'erp_processing_process_technology' AS new_field, 'Excel列名：加工工艺' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_加工方式' AS old_field, 'erp_processing_method' AS new_field, 'Excel列名：加工方式' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_加工方式（重复列2）' AS old_field, 'erp_processing_method_duplicate_2' AS new_field, 'Excel列名：加工方式' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_单价' AS old_field, 'erp_unit_price' AS new_field, 'Excel列名：单价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_单位' AS old_field, 'erp_unit' AS new_field, 'Excel列名：单位' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_厂内编号' AS old_field, 'erp_internal_product_no' AS new_field, 'Excel列名：厂内编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_合作方式' AS old_field, 'erp_cooperation_method' AS new_field, 'Excel列名：合作方式' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_合计金额' AS old_field, 'erp_total_amount' AS new_field, 'Excel列名：合计金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_含税单价' AS old_field, 'erp_tax_inclusive_unit_price' AS new_field, 'Excel列名：含税单价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_含税类别' AS old_field, 'erp_tax_inclusive_category' AS new_field, 'Excel列名：含税类别' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_含税金额' AS old_field, 'erp_tax_inclusive_amount' AS new_field, 'Excel列名：含税金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_含税金额(本位币)' AS old_field, 'erp_tax_inclusive_amount_local_currency' AS new_field, 'Excel列名：含税金额(本位币)' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_回复交期' AS old_field, 'erp_reply_delivery_date' AS new_field, 'Excel列名：回复交期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_备品数量' AS old_field, 'erp_spare_quantity' AS new_field, 'Excel列名：备品数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_客户' AS old_field, 'erp_customer' AS new_field, 'Excel列名：客户' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_客户PO' AS old_field, 'erp_customer_po' AS new_field, 'Excel列名：客户PO' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_客户PO_2' AS old_field, 'erp_customer_po_2' AS new_field, 'Excel列名：客户PO_2' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_客户料号' AS old_field, 'erp_customer_part_no' AS new_field, 'Excel列名：客户料号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_客户级别' AS old_field, 'erp_customer_grade' AS new_field, 'Excel列名：客户级别' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_客户编号' AS old_field, 'erp_customer_code' AS new_field, 'Excel列名：客户编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_层数' AS old_field, 'erp_layer_count' AS new_field, 'Excel列名：层数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_工程拼板宽' AS old_field, 'erp_engineering_panelization_width' AS new_field, 'Excel列名：工程拼板宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_工程拼板数' AS old_field, 'erp_engineering_panelization_count' AS new_field, 'Excel列名：工程拼板数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_工程拼板长' AS old_field, 'erp_engineering_panelization_length' AS new_field, 'Excel列名：工程拼板长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_工程费' AS old_field, 'erp_engineering_fee' AS new_field, 'Excel列名：工程费' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_币别' AS old_field, 'erp_currency' AS new_field, 'Excel列名：币别' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_平方单价' AS old_field, 'erp_square_meters_unit_price' AS new_field, 'Excel列名：平方单价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_平米价(原币)' AS old_field, 'erp_square_meters_price_original_currency' AS new_field, 'Excel列名：平米价(原币)' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_库存零品' AS old_field, 'erp_inventory_loose_pieces' AS new_field, 'Excel列名：库存零品' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_成型方式' AS old_field, 'erp_forming_method' AS new_field, 'Excel列名：成型方式' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_报价拼板宽' AS old_field, 'erp_quotation_panelization_width' AS new_field, 'Excel列名：报价拼板宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_报价拼板数' AS old_field, 'erp_quotation_panelization_count' AS new_field, 'Excel列名：报价拼板数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_报价拼板长' AS old_field, 'erp_quotation_panelization_length' AS new_field, 'Excel列名：报价拼板长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_新单/返单' AS old_field, 'erp_new_order_repeat_order' AS new_field, 'Excel列名：新单/返单' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_未转用的口头订单数量' AS old_field, 'erp_not_reallocation_of_verbal_order_quantity' AS new_field, 'Excel列名：未转用的口头订单数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_材质' AS old_field, 'erp_material' AS new_field, 'Excel列名：材质' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_板厚' AS old_field, 'erp_board_thickness' AS new_field, 'Excel列名：板厚' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_模具费' AS old_field, 'erp_mold_fee' AS new_field, 'Excel列名：模具费' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_欠交货量' AS old_field, 'erp_outstanding_delivery_quantity' AS new_field, 'Excel列名：欠交货量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_汇率' AS old_field, 'erp_exchange_rate' AS new_field, 'Excel列名：汇率' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_测试方式' AS old_field, 'erp_testing_method' AS new_field, 'Excel列名：测试方式' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_测试费' AS old_field, 'erp_testing_fee' AS new_field, 'Excel列名：测试费' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_物料编码' AS old_field, 'erp_material_code' AS new_field, 'Excel列名：物料编码' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_生产投料数量' AS old_field, 'erp_production_material_input_quantity' AS new_field, 'Excel列名：生产投料数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_累计交货量' AS old_field, 'erp_cumulative_delivery_quantity' AS new_field, 'Excel列名：累计交货量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_累计外包金额' AS old_field, 'erp_cumulative_subcontract_amount' AS new_field, 'Excel列名：累计外包金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_累计生产通知单投料' AS old_field, 'erp_cumulative_production_notice_material_input' AS new_field, 'Excel列名：累计生产通知单投料' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_终端料号' AS old_field, 'erp_end_customer_part_no' AS new_field, 'Excel列名：终端料号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_菲林费' AS old_field, 'erp_film_fee' AS new_field, 'Excel列名：菲林费' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_被转用数量' AS old_field, 'erp_by_reallocation_quantity' AS new_field, 'Excel列名：被转用数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_计划外包数量' AS old_field, 'erp_planned_subcontract_quantity' AS new_field, 'Excel列名：计划外包数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_订单加急' AS old_field, 'erp_order_urgent' AS new_field, 'Excel列名：订单加急' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_订单备注' AS old_field, 'erp_order_remarks' AS new_field, 'Excel列名：订单备注' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_订单库存数量' AS old_field, 'erp_order_inventory_quantity' AS new_field, 'Excel列名：订单库存数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_订单状态' AS old_field, 'erp_order_status' AS new_field, 'Excel列名：订单状态' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_订单编号' AS old_field, 'erp_order_no' AS new_field, 'Excel列名：订单编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_订单附件' AS old_field, 'erp_order_attachments' AS new_field, 'Excel列名：订单附件' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_跟单文员' AS old_field, 'erp_order_clerk' AS new_field, 'Excel列名：跟单文员' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_转用数量' AS old_field, 'erp_reallocation_quantity' AS new_field, 'Excel列名：转用数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_输入日期' AS old_field, 'erp_entry_date' AS new_field, 'Excel列名：输入日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_输入者' AS old_field, 'erp_entered_by' AS new_field, 'Excel列名：输入者' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_连片宽' AS old_field, 'erp_array_width' AS new_field, 'Excel列名：连片宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_连片数' AS old_field, 'erp_array_count' AS new_field, 'Excel列名：连片数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_连片长' AS old_field, 'erp_array_length' AS new_field, 'Excel列名：连片长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_order' AS table_name, 'erp_铜厚' AS old_field, 'erp_copper_thickness' AS new_field, 'Excel列名：铜厚' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_part' AS table_name, 'erp_PCS宽' AS old_field, 'erp_pcs_width' AS new_field, 'Excel列名：PCS宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_part' AS table_name, 'erp_PCS长' AS old_field, 'erp_pcs_length' AS new_field, 'Excel列名：PCS长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_part' AS table_name, 'erp_单价' AS old_field, 'erp_unit_price' AS new_field, 'Excel列名：单价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_part' AS table_name, 'erp_单位' AS old_field, 'erp_unit' AS new_field, 'Excel列名：单位' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_part' AS table_name, 'erp_单重(克)' AS old_field, 'erp_unit_weight_grams' AS new_field, 'Excel列名：单重(克)' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_part' AS table_name, 'erp_单重输入日期' AS old_field, 'erp_unit_weight_entry_date' AS new_field, 'Excel列名：单重输入日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_part' AS table_name, 'erp_单重输入者' AS old_field, 'erp_unit_weight_entered_by' AS new_field, 'Excel列名：单重输入者' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_part' AS table_name, 'erp_厂内编号' AS old_field, 'erp_internal_product_no' AS new_field, 'Excel列名：厂内编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_part' AS table_name, 'erp_存储仓位' AS old_field, 'erp_storage_bin' AS new_field, 'Excel列名：存储仓位' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_part' AS table_name, 'erp_客户料号' AS old_field, 'erp_customer_part_no' AS new_field, 'Excel列名：客户料号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_part' AS table_name, 'erp_客户编号' AS old_field, 'erp_customer_code' AS new_field, 'Excel列名：客户编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_part' AS table_name, 'erp_层数' AS old_field, 'erp_layer_count' AS new_field, 'Excel列名：层数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_part' AS table_name, 'erp_工程拼板含PCS数' AS old_field, 'erp_engineering_panelization_containing_pcs_count' AS new_field, 'Excel列名：工程拼板含PCS数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_part' AS table_name, 'erp_工程拼板宽' AS old_field, 'erp_engineering_panelization_width' AS new_field, 'Excel列名：工程拼板宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_part' AS table_name, 'erp_工程拼板长' AS old_field, 'erp_engineering_panelization_length' AS new_field, 'Excel列名：工程拼板长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_part' AS table_name, 'erp_工艺' AS old_field, 'erp_process_technology' AS new_field, 'Excel列名：工艺' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_part' AS table_name, 'erp_币别' AS old_field, 'erp_currency' AS new_field, 'Excel列名：币别' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_part' AS table_name, 'erp_平方单价' AS old_field, 'erp_square_meters_unit_price' AS new_field, 'Excel列名：平方单价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_part' AS table_name, 'erp_平米数' AS old_field, 'erp_square_meters' AS new_field, 'Excel列名：平米数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_part' AS table_name, 'erp_成品厚度' AS old_field, 'erp_finished_goods_thickness' AS new_field, 'Excel列名：成品厚度' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_part' AS table_name, 'erp_成品库存' AS old_field, 'erp_finished_goods_inventory' AS new_field, 'Excel列名：成品库存' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_part' AS table_name, 'erp_成品铜厚' AS old_field, 'erp_finished_goods_copper_thickness' AS new_field, 'Excel列名：成品铜厚' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_part' AS table_name, 'erp_成本金额<本位币>' AS old_field, 'erp_cost_amount_local_currency' AS new_field, 'Excel列名：成本金额<本位币>' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_part' AS table_name, 'erp_报价拼板含PCS数' AS old_field, 'erp_quotation_panelization_containing_pcs_count' AS new_field, 'Excel列名：报价拼板含PCS数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_part' AS table_name, 'erp_报价拼板宽' AS old_field, 'erp_quotation_panelization_width' AS new_field, 'Excel列名：报价拼板宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_part' AS table_name, 'erp_报价拼板长' AS old_field, 'erp_quotation_panelization_length' AS new_field, 'Excel列名：报价拼板长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_part' AS table_name, 'erp_料号附件' AS old_field, 'erp_part_no_attachments' AS new_field, 'Excel列名：料号附件' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_part' AS table_name, 'erp_本币单价' AS old_field, 'erp_local_currency_unit_price' AS new_field, 'Excel列名：本币单价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_part' AS table_name, 'erp_材质' AS old_field, 'erp_material' AS new_field, 'Excel列名：材质' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_part' AS table_name, 'erp_目前零品库存' AS old_field, 'erp_current_loose_pieces_inventory' AS new_field, 'Excel列名：目前零品库存' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_part' AS table_name, 'erp_终端料号' AS old_field, 'erp_end_customer_part_no' AS new_field, 'Excel列名：终端料号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_part' AS table_name, 'erp_营销模式' AS old_field, 'erp_business_model' AS new_field, 'Excel列名：营销模式' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_part' AS table_name, 'erp_连片宽' AS old_field, 'erp_array_width' AS new_field, 'Excel列名：连片宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_part' AS table_name, 'erp_连片数' AS old_field, 'erp_array_count' AS new_field, 'Excel列名：连片数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_customer_part' AS table_name, 'erp_连片长' AS old_field, 'erp_array_length' AS new_field, 'Excel列名：连片长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_37' AS old_field, 'erp_column_37' AS new_field, 'Excel列名：37' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_下单数量' AS old_field, 'erp_order_placed_quantity' AS new_field, 'Excel列名：下单数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_不补不换' AS old_field, 'erp_no_replacement' AS new_field, 'Excel列名：不补不换' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_业务员' AS old_field, 'erp_salesperson' AS new_field, 'Excel列名：业务员' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_交货数量' AS old_field, 'erp_delivery_quantity' AS new_field, 'Excel列名：交货数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_交货数量（重复列2）' AS old_field, 'erp_delivery_quantity_duplicate_2' AS new_field, 'Excel列名：交货数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_交货方式' AS old_field, 'erp_delivery_method' AS new_field, 'Excel列名：交货方式' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_其它费' AS old_field, 'erp_other_fee' AS new_field, 'Excel列名：其它费' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_出库面积(平米)' AS old_field, 'erp_issue_area_square_meters' AS new_field, 'Excel列名：出库面积(平米)' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_出货发票号' AS old_field, 'erp_shipment_invoice_no' AS new_field, 'Excel列名：出货发票号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_制令单号' AS old_field, 'erp_production_order_no' AS new_field, 'Excel列名：制令单号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_单价' AS old_field, 'erp_unit_price' AS new_field, 'Excel列名：单价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_单位' AS old_field, 'erp_unit' AS new_field, 'Excel列名：单位' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_单号' AS old_field, 'erp_document_no' AS new_field, 'Excel列名：单号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_厂内编号' AS old_field, 'erp_internal_product_no' AS new_field, 'Excel列名：厂内编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_各项费用小计' AS old_field, 'erp_itemized_expense_subtotal' AS new_field, 'Excel列名：各项费用小计' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_含税单价' AS old_field, 'erp_tax_inclusive_unit_price' AS new_field, 'Excel列名：含税单价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_含税金额' AS old_field, 'erp_tax_inclusive_amount' AS new_field, 'Excel列名：含税金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_周期' AS old_field, 'erp_cycle' AS new_field, 'Excel列名：周期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_增值税金额' AS old_field, 'erp_vat_amount' AS new_field, 'Excel列名：增值税金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_备注说明' AS old_field, 'erp_remarks_description' AS new_field, 'Excel列名：备注说明' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_客户公司全称' AS old_field, 'erp_customer_company_full_name' AS new_field, 'Excel列名：客户公司全称' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_客户发票全称' AS old_field, 'erp_customer_invoice_full_name' AS new_field, 'Excel列名：客户发票全称' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_客户名称' AS old_field, 'erp_customer_name' AS new_field, 'Excel列名：客户名称' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_层数' AS old_field, 'erp_layer_count' AS new_field, 'Excel列名：层数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_工程费' AS old_field, 'erp_engineering_fee' AS new_field, 'Excel列名：工程费' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_币别' AS old_field, 'erp_currency' AS new_field, 'Excel列名：币别' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_总金额' AS old_field, 'erp_total_amount' AS new_field, 'Excel列名：总金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_收费/免费' AS old_field, 'erp_charged_free' AS new_field, 'Excel列名：收费/免费' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_未含税单价' AS old_field, 'erp_tax_exclusive_unit_price' AS new_field, 'Excel列名：未含税单价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_未含税金额' AS old_field, 'erp_tax_exclusive_amount' AS new_field, 'Excel列名：未含税金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_本位币金额' AS old_field, 'erp_local_currency_amount' AS new_field, 'Excel列名：本位币金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_模具费' AS old_field, 'erp_mold_fee' AS new_field, 'Excel列名：模具费' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_欠补货金额' AS old_field, 'erp_outstanding_replenishment_amount' AS new_field, 'Excel列名：欠补货金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_欠补货金额(本币)' AS old_field, 'erp_outstanding_replenishment_amount_local_currency' AS new_field, 'Excel列名：欠补货金额(本币)' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_测试费' AS old_field, 'erp_testing_fee' AS new_field, 'Excel列名：测试费' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_海关商品名称' AS old_field, 'erp_customs_commodity_name' AS new_field, 'Excel列名：海关商品名称' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_海关商品编码' AS old_field, 'erp_customs_commodity_code' AS new_field, 'Excel列名：海关商品编码' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_累计交货' AS old_field, 'erp_cumulative_delivery' AS new_field, 'Excel列名：累计交货' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_终端料号' AS old_field, 'erp_end_customer_part_no' AS new_field, 'Excel列名：终端料号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_菲林费' AS old_field, 'erp_film_fee' AS new_field, 'Excel列名：菲林费' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_订单_mc1' AS old_field, 'erp_order_mc_1' AS new_field, 'Excel列名：订单_mc1' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_订单其他单价1' AS old_field, 'erp_order_other_unit_price_1' AS new_field, 'Excel列名：订单其他单价1' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_订单其他单价2' AS old_field, 'erp_order_other_unit_price_2' AS new_field, 'Excel列名：订单其他单价2' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_货物暂存本厂' AS old_field, 'erp_goods_temporary_storage_this_factory' AS new_field, 'Excel列名：货物暂存本厂' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_贸易' AS old_field, 'erp_trade' AS new_field, 'Excel列名：贸易' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_贸易单价' AS old_field, 'erp_trade_unit_price' AS new_field, 'Excel列名：贸易单价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_贸易单号' AS old_field, 'erp_trade_document_no' AS new_field, 'Excel列名：贸易单号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_跟单员' AS old_field, 'erp_order_coordinator' AS new_field, 'Excel列名：跟单员' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_连片宽' AS old_field, 'erp_array_width' AS new_field, 'Excel列名：连片宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_连片数' AS old_field, 'erp_array_count' AS new_field, 'Excel列名：连片数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_连片长' AS old_field, 'erp_array_length' AS new_field, 'Excel列名：连片长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_退货价类别' AS old_field, 'erp_return_price_category' AS new_field, 'Excel列名：退货价类别' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_送货单号' AS old_field, 'erp_delivery_note_no' AS new_field, 'Excel列名：送货单号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_送货日期' AS old_field, 'erp_delivery_date' AS new_field, 'Excel列名：送货日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_delivery_note' AS table_name, 'erp_金额' AS old_field, 'erp_amount' AS new_field, 'Excel列名：金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_A板含PCS' AS old_field, 'erp_a_board_containing_pcs' AS new_field, 'Excel列名：A板含PCS' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_BOM用量' AS old_field, 'erp_bom_consumption' AS new_field, 'Excel列名：BOM用量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_B板含PCS' AS old_field, 'erp_b_board_containing_pcs' AS new_field, 'Excel列名：B板含PCS' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_C板含PCS' AS old_field, 'erp_c_board_containing_pcs' AS new_field, 'Excel列名：C板含PCS' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_D板含PCS' AS old_field, 'erp_d_board_containing_pcs' AS new_field, 'Excel列名：D板含PCS' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_MI_ID' AS old_field, 'erp_mi_id' AS new_field, 'Excel列名：MI_ID' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_MI停止/判退原因' AS old_field, 'erp_mi_stop_rejection_reason' AS new_field, 'Excel列名：MI停止/判退原因' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_MI创建日期' AS old_field, 'erp_mi_creation_date' AS new_field, 'Excel列名：MI创建日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_MI创建者' AS old_field, 'erp_mi_created_by' AS new_field, 'Excel列名：MI创建者' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_MI异常说明' AS old_field, 'erp_mi_abnormal_description' AS new_field, 'Excel列名：MI异常说明' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_PNL-A宽' AS old_field, 'erp_pnl_a_width' AS new_field, 'Excel列名：PNL-A宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_PNL-A宽含SET数' AS old_field, 'erp_pnl_a_width_containing_set_count' AS new_field, 'Excel列名：PNL-A宽含SET数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_PNL-A数量' AS old_field, 'erp_pnl_a_quantity' AS new_field, 'Excel列名：PNL-A数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_PNL-A长' AS old_field, 'erp_pnl_a_length' AS new_field, 'Excel列名：PNL-A长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_PNL-A长含SET数' AS old_field, 'erp_pnl_a_length_containing_set_count' AS new_field, 'Excel列名：PNL-A长含SET数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_PNL-B宽' AS old_field, 'erp_pnl_b_width' AS new_field, 'Excel列名：PNL-B宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_PNL-B宽含SET数' AS old_field, 'erp_pnl_b_width_containing_set_count' AS new_field, 'Excel列名：PNL-B宽含SET数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_PNL-B数量' AS old_field, 'erp_pnl_b_quantity' AS new_field, 'Excel列名：PNL-B数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_PNL-B长' AS old_field, 'erp_pnl_b_length' AS new_field, 'Excel列名：PNL-B长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_PNL-B长含SET数' AS old_field, 'erp_pnl_b_length_containing_set_count' AS new_field, 'Excel列名：PNL-B长含SET数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_PNL-C宽' AS old_field, 'erp_pnl_c_width' AS new_field, 'Excel列名：PNL-C宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_PNL-C宽含SET数' AS old_field, 'erp_pnl_c_width_containing_set_count' AS new_field, 'Excel列名：PNL-C宽含SET数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_PNL-C数量' AS old_field, 'erp_pnl_c_quantity' AS new_field, 'Excel列名：PNL-C数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_PNL-C长' AS old_field, 'erp_pnl_c_length' AS new_field, 'Excel列名：PNL-C长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_PNL-C长含SET数' AS old_field, 'erp_pnl_c_length_containing_set_count' AS new_field, 'Excel列名：PNL-C长含SET数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_PNL-D宽' AS old_field, 'erp_pnl_d_width' AS new_field, 'Excel列名：PNL-D宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_PNL-D宽含SET数' AS old_field, 'erp_pnl_d_width_containing_set_count' AS new_field, 'Excel列名：PNL-D宽含SET数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_PNL-D数量' AS old_field, 'erp_pnl_d_quantity' AS new_field, 'Excel列名：PNL-D数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_PNL-D长' AS old_field, 'erp_pnl_d_length' AS new_field, 'Excel列名：PNL-D长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_PNL-D长含SET数' AS old_field, 'erp_pnl_d_length_containing_set_count' AS new_field, 'Excel列名：PNL-D长含SET数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_QAE审核OK_NG' AS old_field, 'erp_qae_review_ok_ng' AS new_field, 'Excel列名：QAE审核OK_NG' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_QAE审核人' AS old_field, 'erp_qae_review_person' AS new_field, 'Excel列名：QAE审核人' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_QAE审核日期' AS old_field, 'erp_qae_review_date' AS new_field, 'Excel列名：QAE审核日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_SET利用率%' AS old_field, 'erp_set_utilization_rate_percent' AS new_field, 'Excel列名：SET利用率%' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_SET含PCS数' AS old_field, 'erp_set_containing_pcs_count' AS new_field, 'Excel列名：SET含PCS数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_SET宽' AS old_field, 'erp_set_width' AS new_field, 'Excel列名：SET宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_SET宽含PCS数' AS old_field, 'erp_set_width_containing_pcs_count' AS new_field, 'Excel列名：SET宽含PCS数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_SET长' AS old_field, 'erp_set_length' AS new_field, 'Excel列名：SET长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_SET长含PCS数' AS old_field, 'erp_set_length_containing_pcs_count' AS new_field, 'Excel列名：SET长含PCS数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_bom_pc1' AS old_field, 'erp_bom_pc_1' AS new_field, 'Excel列名：bom_pc1' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_mm1_in2' AS old_field, 'erp_mm_1_in_2' AS new_field, 'Excel列名：mm1_in2' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_产品类型' AS old_field, 'erp_product_type' AS new_field, 'Excel列名：产品类型' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_修改次数' AS old_field, 'erp_revision_count' AS new_field, 'Excel列名：修改次数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_制作要求/原料名称_规格' AS old_field, 'erp_manufacturing_required_material_name_specification' AS new_field, 'Excel列名：制作要求/原料名称_规格' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_厂内编号' AS old_field, 'erp_internal_product_no' AS new_field, 'Excel列名：厂内编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_发放/停止' AS old_field, 'erp_release_stop' AS new_field, 'Excel列名：发放/停止' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_发行日期' AS old_field, 'erp_issue_date' AS new_field, 'Excel列名：发行日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_合拼厂内编号' AS old_field, 'erp_combined_panel_internal_product_no' AS new_field, 'Excel列名：合拼厂内编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_字符菲林编号' AS old_field, 'erp_legend_film_no' AS new_field, 'Excel列名：字符菲林编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_审批OK_NG' AS old_field, 'erp_approval_ok_ng' AS new_field, 'Excel列名：审批OK_NG' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_审批人' AS old_field, 'erp_approval_person' AS new_field, 'Excel列名：审批人' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_审批日期D' AS old_field, 'erp_approval_date_d' AS new_field, 'Excel列名：审批日期D' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_审核人' AS old_field, 'erp_review_person' AS new_field, 'Excel列名：审核人' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_审核日期' AS old_field, 'erp_review_date' AS new_field, 'Excel列名：审核日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_客户代号' AS old_field, 'erp_customer_code' AS new_field, 'Excel列名：客户代号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_客户料号' AS old_field, 'erp_customer_part_no' AS new_field, 'Excel列名：客户料号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_客户简称' AS old_field, 'erp_customer_short_name' AS new_field, 'Excel列名：客户简称' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_层数' AS old_field, 'erp_layer_count' AS new_field, 'Excel列名：层数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_工作板利用率%' AS old_field, 'erp_panel_utilization_rate_percent' AS new_field, 'Excel列名：工作板利用率%' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_工序名称' AS old_field, 'erp_process_name' AS new_field, 'Excel列名：工序名称' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_工艺' AS old_field, 'erp_process_technology' AS new_field, 'Excel列名：工艺' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_总SET数' AS old_field, 'erp_total_set_count' AS new_field, 'Excel列名：总SET数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_总工作板数' AS old_field, 'erp_total_panel_count' AS new_field, 'Excel列名：总工作板数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_成品利用率%' AS old_field, 'erp_finished_goods_utilization_rate_percent' AS new_field, 'Excel列名：成品利用率%' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_成型方式' AS old_field, 'erp_forming_method' AS new_field, 'Excel列名：成型方式' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_指定厂牌' AS old_field, 'erp_designated_brand' AS new_field, 'Excel列名：指定厂牌' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_排版图转码ok' AS old_field, 'erp_panelization_drawing_conversion_ok' AS new_field, 'Excel列名：排版图转码ok' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_排版数量' AS old_field, 'erp_panelization_quantity' AS new_field, 'Excel列名：排版数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_排版说明' AS old_field, 'erp_panelization_description' AS new_field, 'Excel列名：排版说明' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_无卤素' AS old_field, 'erp_halogen_free' AS new_field, 'Excel列名：无卤素' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_最新版资料' AS old_field, 'erp_latest_version_data' AS new_field, 'Excel列名：最新版资料' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_有无水印' AS old_field, 'erp_has_watermark' AS new_field, 'Excel列名：有无水印' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_材质' AS old_field, 'erp_material' AS new_field, 'Excel列名：材质' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_板厚' AS old_field, 'erp_board_thickness' AS new_field, 'Excel列名：板厚' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_板材CTE值' AS old_field, 'erp_board_material_cte_value' AS new_field, 'Excel列名：板材CTE值' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_板材CTI值' AS old_field, 'erp_board_material_cti_value' AS new_field, 'Excel列名：板材CTI值' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_板材TD值' AS old_field, 'erp_board_material_td_value' AS new_field, 'Excel列名：板材TD值' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_板材TG值' AS old_field, 'erp_board_material_tg_value' AS new_field, 'Excel列名：板材TG值' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_板材型号' AS old_field, 'erp_board_material_model' AS new_field, 'Excel列名：板材型号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_板材宽' AS old_field, 'erp_board_material_width' AS new_field, 'Excel列名：板材宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_板材长' AS old_field, 'erp_board_material_length' AS new_field, 'Excel列名：板材长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_样板编号' AS old_field, 'erp_sample_no' AS new_field, 'Excel列名：样板编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_模具编号' AS old_field, 'erp_mold_no' AS new_field, 'Excel列名：模具编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_版本号' AS old_field, 'erp_version' AS new_field, 'Excel列名：版本号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_物料编号' AS old_field, 'erp_material_no' AS new_field, 'Excel列名：物料编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_特殊工艺说明' AS old_field, 'erp_special_process_technology_description' AS new_field, 'Excel列名：特殊工艺说明' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_环保' AS old_field, 'erp_environmental_compliance' AS new_field, 'Excel列名：环保' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_生产难易程度' AS old_field, 'erp_production_difficulty' AS new_field, 'Excel列名：生产难易程度' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_签名' AS old_field, 'erp_signature' AS new_field, 'Excel列名：签名' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_线路菲林编号' AS old_field, 'erp_circuit_film_no' AS new_field, 'Excel列名：线路菲林编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_结构工艺' AS old_field, 'erp_structure_technology' AS new_field, 'Excel列名：结构工艺' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_输入日期' AS old_field, 'erp_entry_date' AS new_field, 'Excel列名：输入日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_输入者' AS old_field, 'erp_entered_by' AS new_field, 'Excel列名：输入者' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_铜箔' AS old_field, 'erp_copper_foil' AS new_field, 'Excel列名：铜箔' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_阻焊菲林编号' AS old_field, 'erp_solder_mask_film_no' AS new_field, 'Excel列名：阻焊菲林编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_engineering_data' AS table_name, 'erp_首选排版方式' AS old_field, 'erp_preferred_panelization_method' AS new_field, 'Excel列名：首选排版方式' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_PCS/箱' AS old_field, 'erp_pcs_carton' AS new_field, 'Excel列名：PCS/箱' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_\\结余面积' AS old_field, 'erp_balance_area' AS new_field, 'Excel列名：\\结余面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_产品ID' AS old_field, 'erp_product_id' AS new_field, 'Excel列名：产品ID' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_人工成本单价' AS old_field, 'erp_labor_cost_unit_price' AS new_field, 'Excel列名：人工成本单价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_人工成本金额' AS old_field, 'erp_labor_cost_amount' AS new_field, 'Excel列名：人工成本金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_入库ID_b' AS old_field, 'erp_receipt_id_b' AS new_field, 'Excel列名：入库ID_b' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_入库ID_m' AS old_field, 'erp_receipt_id_m' AS new_field, 'Excel列名：入库ID_m' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_入库mb1' AS old_field, 'erp_receipt_mb_1' AS new_field, 'Excel列名：入库mb1' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_入库mb2' AS old_field, 'erp_receipt_mb_2' AS new_field, 'Excel列名：入库mb2' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_入库mc4' AS old_field, 'erp_receipt_mc_4' AS new_field, 'Excel列名：入库mc4' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_入库mm1' AS old_field, 'erp_receipt_mm_1' AS new_field, 'Excel列名：入库mm1' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_入库mm2' AS old_field, 'erp_receipt_mm_2' AS new_field, 'Excel列名：入库mm2' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_入库不含税单价本币' AS old_field, 'erp_receipt_tax_exclusive_unit_price_local_currency' AS new_field, 'Excel列名：入库不含税单价本币' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_入库不含税金额本币' AS old_field, 'erp_receipt_tax_exclusive_amount_local_currency' AS new_field, 'Excel列名：入库不含税金额本币' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_入库单价' AS old_field, 'erp_receipt_price' AS new_field, 'Excel列名：入库单价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_入库单号' AS old_field, 'erp_receipt_no' AS new_field, 'Excel列名：入库单号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_入库含税单价本币' AS old_field, 'erp_receipt_tax_inclusive_unit_price_local_currency' AS new_field, 'Excel列名：入库含税单价本币' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_入库含税金额本币' AS old_field, 'erp_receipt_tax_inclusive_amount_local_currency' AS new_field, 'Excel列名：入库含税金额本币' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_入库日期' AS old_field, 'erp_receipt_date' AS new_field, 'Excel列名：入库日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_入库日期<含时分>' AS old_field, 'erp_receipt_date_with_time' AS new_field, 'Excel列名：入库日期<含时分>' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_入库类别' AS old_field, 'erp_receipt_category' AS new_field, 'Excel列名：入库类别' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_入库重量' AS old_field, 'erp_receipt_weight' AS new_field, 'Excel列名：入库重量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_入库金额' AS old_field, 'erp_receipt_amount' AS new_field, 'Excel列名：入库金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_入库面积(平方米)' AS old_field, 'erp_receipt_area_square_meters' AS new_field, 'Excel列名：入库面积(平方米)' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_其他mc1' AS old_field, 'erp_mc_1' AS new_field, 'Excel列名：其他mc1' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_其他说明' AS old_field, 'erp_other_description' AS new_field, 'Excel列名：其他说明' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_冻结' AS old_field, 'erp_frozen' AS new_field, 'Excel列名：冻结' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_制费成本单价' AS old_field, 'erp_manufacturing_overhead_cost_unit_price' AS new_field, 'Excel列名：制费成本单价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_制费成本金额' AS old_field, 'erp_manufacturing_overhead_cost_amount' AS new_field, 'Excel列名：制费成本金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_单价(本位币)' AS old_field, 'erp_unit_price_local_currency' AS new_field, 'Excel列名：单价(本位币)' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_单位' AS old_field, 'erp_unit' AS new_field, 'Excel列名：单位' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_单重(G)' AS old_field, 'erp_unit_weight_g' AS new_field, 'Excel列名：单重(G)' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_厂内编号' AS old_field, 'erp_internal_product_no' AS new_field, 'Excel列名：厂内编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_原入库日期' AS old_field, 'erp_original_receipt_date' AS new_field, 'Excel列名：原入库日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_合拼明细ID' AS old_field, 'erp_combined_panel_detail_id' AS new_field, 'Excel列名：合拼明细ID' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_备注' AS old_field, 'erp_remarks' AS new_field, 'Excel列名：备注' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_外包入库单号' AS old_field, 'erp_subcontract_receipt_no' AS new_field, 'Excel列名：外包入库单号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_外包单号' AS old_field, 'erp_subcontract_document_no' AS new_field, 'Excel列名：外包单号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_外包厂商名称' AS old_field, 'erp_subcontract_supplier_name' AS new_field, 'Excel列名：外包厂商名称' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_外包厂商编号' AS old_field, 'erp_subcontract_supplier_no' AS new_field, 'Excel列名：外包厂商编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_外箱条码' AS old_field, 'erp_outer_carton_barcode' AS new_field, 'Excel列名：外箱条码' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_客户ID' AS old_field, 'erp_customer_id' AS new_field, 'Excel列名：客户ID' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_客户名称' AS old_field, 'erp_customer_name' AS new_field, 'Excel列名：客户名称' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_客户料号' AS old_field, 'erp_customer_part_no' AS new_field, 'Excel列名：客户料号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_客户编号' AS old_field, 'erp_customer_code' AS new_field, 'Excel列名：客户编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_客户订单ID_b' AS old_field, 'erp_customer_order_id_b' AS new_field, 'Excel列名：客户订单ID_b' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_客户订单ID_m' AS old_field, 'erp_customer_order_id_m' AS new_field, 'Excel列名：客户订单ID_m' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_层数' AS old_field, 'erp_layer_count' AS new_field, 'Excel列名：层数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_工单号' AS old_field, 'erp_work_order_no' AS new_field, 'Excel列名：工单号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_币别' AS old_field, 'erp_currency' AS new_field, 'Excel列名：币别' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_待返工' AS old_field, 'erp_pending_rework' AS new_field, 'Excel列名：待返工' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_成品1零品2' AS old_field, 'erp_finished_goods_1_loose_pieces_2' AS new_field, 'Excel列名：成品1零品2' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_成品利用率' AS old_field, 'erp_finished_goods_utilization_rate' AS new_field, 'Excel列名：成品利用率' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_成品库存' AS old_field, 'erp_finished_goods_inventory' AS new_field, 'Excel列名：成品库存' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_成品库存金额' AS old_field, 'erp_finished_goods_inventory_amount' AS new_field, 'Excel列名：成品库存金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_成型方式' AS old_field, 'erp_forming_method' AS new_field, 'Excel列名：成型方式' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_成本加工价' AS old_field, 'erp_cost_processing_price' AS new_field, 'Excel列名：成本加工价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_成本加工金额' AS old_field, 'erp_cost_processing_amount' AS new_field, 'Excel列名：成本加工金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_成本单价' AS old_field, 'erp_cost_unit_price' AS new_field, 'Excel列名：成本单价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_成本外发价' AS old_field, 'erp_cost_outsourcing_price' AS new_field, 'Excel列名：成本外发价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_成本外发金额' AS old_field, 'erp_cost_outsourcing_amount' AS new_field, 'Excel列名：成本外发金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_成本摊销价' AS old_field, 'erp_cost_amortization_price' AS new_field, 'Excel列名：成本摊销价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_成本摊销金额' AS old_field, 'erp_cost_amortization_amount' AS new_field, 'Excel列名：成本摊销金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_成本板材价' AS old_field, 'erp_cost_board_material_price' AS new_field, 'Excel列名：成本板材价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_成本板材金额' AS old_field, 'erp_cost_board_material_amount' AS new_field, 'Excel列名：成本板材金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_成本金额' AS old_field, 'erp_cost_amount' AS new_field, 'Excel列名：成本金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_所属年月' AS old_field, 'erp_associated_year_month' AS new_field, 'Excel列名：所属年月' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_投料类别' AS old_field, 'erp_material_input_category' AS new_field, 'Excel列名：投料类别' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_投料面积' AS old_field, 'erp_material_input_area' AS new_field, 'Excel列名：投料面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_折旧成本单价' AS old_field, 'erp_depreciation_cost_unit_price' AS new_field, 'Excel列名：折旧成本单价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_折旧成本金额' AS old_field, 'erp_depreciation_cost_amount' AS new_field, 'Excel列名：折旧成本金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_旧厂内编号' AS old_field, 'erp_old_internal_product_no' AS new_field, 'Excel列名：旧厂内编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_有PO数量' AS old_field, 'erp_with_po_quantity' AS new_field, 'Excel列名：有PO数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_本次入库量' AS old_field, 'erp_current_receipt_quantity' AS new_field, 'Excel列名：本次入库量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_材质' AS old_field, 'erp_material' AS new_field, 'Excel列名：材质' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_板材厚度' AS old_field, 'erp_board_material_thickness' AS new_field, 'Excel列名：板材厚度' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_板材面积(利用率)' AS old_field, 'erp_board_material_area_utilization_rate' AS new_field, 'Excel列名：板材面积(利用率)' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_毛利润率%' AS old_field, 'erp_gross_margin_rate_percent' AS new_field, 'Excel列名：毛利润率%' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_水费成本单价' AS old_field, 'erp_water_cost_unit_price' AS new_field, 'Excel列名：水费成本单价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_水费成本金额' AS old_field, 'erp_water_cost_amount' AS new_field, 'Excel列名：水费成本金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_物料编号' AS old_field, 'erp_material_no' AS new_field, 'Excel列名：物料编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_班次' AS old_field, 'erp_shift' AS new_field, 'Excel列名：班次' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_生产bcn5' AS old_field, 'erp_production_bcn_5' AS new_field, 'Excel列名：生产bcn5' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_生产bcn6' AS old_field, 'erp_production_bcn_6' AS new_field, 'Excel列名：生产bcn6' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_生产bcn7' AS old_field, 'erp_production_bcn_7' AS new_field, 'Excel列名：生产bcn7' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_生产bcn8' AS old_field, 'erp_production_bcn_8' AS new_field, 'Excel列名：生产bcn8' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_生产周期' AS old_field, 'erp_production_cycle' AS new_field, 'Excel列名：生产周期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_生产工厂' AS old_field, 'erp_production_factory' AS new_field, 'Excel列名：生产工厂' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_生产工艺' AS old_field, 'erp_production_process_technology' AS new_field, 'Excel列名：生产工艺' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_生产指令ID' AS old_field, 'erp_production_order_id' AS new_field, 'Excel列名：生产指令ID' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_电费成本单价' AS old_field, 'erp_electricity_cost_unit_price' AS new_field, 'Excel列名：电费成本单价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_电费成本金额' AS old_field, 'erp_electricity_cost_amount' AS new_field, 'Excel列名：电费成本金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_箱号' AS old_field, 'erp_carton_no' AS new_field, 'Excel列名：箱号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_累计入库面积' AS old_field, 'erp_cumulative_receipt_area' AS new_field, 'Excel列名：累计入库面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_累计报废面积' AS old_field, 'erp_cumulative_scrap_area' AS new_field, 'Excel列名：累计报废面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_累计领料量' AS old_field, 'erp_cumulative_material_issue_quantity' AS new_field, 'Excel列名：累计领料量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_结余数量' AS old_field, 'erp_balance_quantity' AS new_field, 'Excel列名：结余数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_结余金额' AS old_field, 'erp_balance_amount' AS new_field, 'Excel列名：结余金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_综合利用率' AS old_field, 'erp_combined_utilization_rate' AS new_field, 'Excel列名：综合利用率' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_转用零品数量' AS old_field, 'erp_reallocation_loose_pieces_quantity' AS new_field, 'Excel列名：转用零品数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_输入日期' AS old_field, 'erp_entry_date' AS new_field, 'Excel列名：输入日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_输入者' AS old_field, 'erp_entered_by' AS new_field, 'Excel列名：输入者' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_连片PCS数' AS old_field, 'erp_array_pcs_count' AS new_field, 'Excel列名：连片PCS数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_连片宽' AS old_field, 'erp_array_width' AS new_field, 'Excel列名：连片宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_连片长' AS old_field, 'erp_array_length' AS new_field, 'Excel列名：连片长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_退货数量' AS old_field, 'erp_return_quantity' AS new_field, 'Excel列名：退货数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_部门名称' AS old_field, 'erp_department_name' AS new_field, 'Excel列名：部门名称' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_金额(本位币)' AS old_field, 'erp_amount_local_currency' AS new_field, 'Excel列名：金额(本位币)' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_铜箔厚度' AS old_field, 'erp_copper_foil_thickness' AS new_field, 'Excel列名：铜箔厚度' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_销售单价' AS old_field, 'erp_sales_unit_price' AS new_field, 'Excel列名：销售单价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_销售币别' AS old_field, 'erp_sales_currency' AS new_field, 'Excel列名：销售币别' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_销售金额' AS old_field, 'erp_sales_amount' AS new_field, 'Excel列名：销售金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_零品库存' AS old_field, 'erp_loose_pieces_inventory' AS new_field, 'Excel列名：零品库存' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_零品库存金额' AS old_field, 'erp_loose_pieces_inventory_amount' AS new_field, 'Excel列名：零品库存金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_零品箱位置' AS old_field, 'erp_loose_pieces_carton_position' AS new_field, 'Excel列名：零品箱位置' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_零品箱号' AS old_field, 'erp_loose_pieces_carton_no' AS new_field, 'Excel列名：零品箱号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_finished_goods_receipt' AS table_name, 'erp_零品箱序号' AS old_field, 'erp_loose_pieces_carton_sequence_no' AS new_field, 'Excel列名：零品箱序号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_CTE' AS old_field, 'erp_cte' AS new_field, 'Excel列名：CTE' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_CTI' AS old_field, 'erp_cti' AS new_field, 'Excel列名：CTI' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_REACH' AS old_field, 'erp_reach' AS new_field, 'Excel列名：REACH' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_TD' AS old_field, 'erp_td' AS new_field, 'Excel列名：TD' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_TG' AS old_field, 'erp_tg' AS new_field, 'Excel列名：TG' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_一厂库存' AS old_field, 'erp_factory_1_inventory' AS new_field, 'Excel列名：一厂库存' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_一厂废品库存' AS old_field, 'erp_factory_1_scrap_inventory' AS new_field, 'Excel列名：一厂废品库存' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_七厂库存' AS old_field, 'erp_factory_7_inventory' AS new_field, 'Excel列名：七厂库存' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_不含税报价' AS old_field, 'erp_tax_exclusive_quotation' AS new_field, 'Excel列名：不含税报价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_二厂库存' AS old_field, 'erp_factory_2_inventory' AS new_field, 'Excel列名：二厂库存' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_二厂废品库存' AS old_field, 'erp_factory_2_scrap_inventory' AS new_field, 'Excel列名：二厂废品库存' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_五厂库存' AS old_field, 'erp_factory_5_inventory' AS new_field, 'Excel列名：五厂库存' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_产地' AS old_field, 'erp_origin' AS new_field, 'Excel列名：产地' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_保质天数' AS old_field, 'erp_shelf_life_days' AS new_field, 'Excel列名：保质天数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_储位' AS old_field, 'erp_storage_location' AS new_field, 'Excel列名：储位' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_允许废品入库' AS old_field, 'erp_allow_scrap_receipt' AS new_field, 'Excel列名：允许废品入库' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_六厂库存' AS old_field, 'erp_factory_6_inventory' AS new_field, 'Excel列名：六厂库存' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_其他c6' AS old_field, 'erp_c_6' AS new_field, 'Excel列名：其他c6' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_加权单价' AS old_field, 'erp_weighted_unit_price' AS new_field, 'Excel列名：加权单价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_单位' AS old_field, 'erp_unit' AS new_field, 'Excel列名：单位' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_单位面积' AS old_field, 'erp_unit_area' AS new_field, 'Excel列名：单位面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_单重' AS old_field, 'erp_unit_weight' AS new_field, 'Excel列名：单重' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_单重输入人' AS old_field, 'erp_unit_weight_entry_person' AS new_field, 'Excel列名：单重输入人' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_单重输入日期' AS old_field, 'erp_unit_weight_entry_date' AS new_field, 'Excel列名：单重输入日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_厂商' AS old_field, 'erp_supplier' AS new_field, 'Excel列名：厂商' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_厂商编号' AS old_field, 'erp_supplier_no' AS new_field, 'Excel列名：厂商编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_厚度' AS old_field, 'erp_thickness' AS new_field, 'Excel列名：厚度' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_原料名称' AS old_field, 'erp_material_name' AS new_field, 'Excel列名：原料名称' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_原料标准名称' AS old_field, 'erp_raw_material_standard_name' AS new_field, 'Excel列名：原料标准名称' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_原料标准规格' AS old_field, 'erp_raw_material_standard_specification' AS new_field, 'Excel列名：原料标准规格' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_原料编号' AS old_field, 'erp_material_no' AS new_field, 'Excel列名：原料编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_大类' AS old_field, 'erp_major_category' AS new_field, 'Excel列名：大类' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_子类' AS old_field, 'erp_subcategory' AS new_field, 'Excel列名：子类' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_存货类别' AS old_field, 'erp_inventory_category' AS new_field, 'Excel列名：存货类别' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_安全库存' AS old_field, 'erp_safety_inventory' AS new_field, 'Excel列名：安全库存' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_安全库存输入日期' AS old_field, 'erp_safety_inventory_entry_date' AS new_field, 'Excel列名：安全库存输入日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_安全库存输入者' AS old_field, 'erp_safety_inventory_entered_by' AS new_field, 'Excel列名：安全库存输入者' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_审核人' AS old_field, 'erp_review_person' AS new_field, 'Excel列名：审核人' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_审核日期' AS old_field, 'erp_review_date' AS new_field, 'Excel列名：审核日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_小类' AS old_field, 'erp_minor_category' AS new_field, 'Excel列名：小类' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_平均不含税单价' AS old_field, 'erp_average_tax_exclusive_unit_price' AS new_field, 'Excel列名：平均不含税单价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_平均单价' AS old_field, 'erp_average_unit_price' AS new_field, 'Excel列名：平均单价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_库存最早入库日期' AS old_field, 'erp_inventory_earliest_receipt_date' AS new_field, 'Excel列名：库存最早入库日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_库存最晚入库日期' AS old_field, 'erp_inventory_latest_receipt_date' AS new_field, 'Excel列名：库存最晚入库日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_库存本币金额' AS old_field, 'erp_inventory_local_currency_amount' AS new_field, 'Excel列名：库存本币金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_库存面积' AS old_field, 'erp_inventory_area' AS new_field, 'Excel列名：库存面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_废品期初库存' AS old_field, 'erp_scrap_opening_inventory' AS new_field, 'Excel列名：废品期初库存' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_废品目前库存' AS old_field, 'erp_scrap_current_inventory' AS new_field, 'Excel列名：废品目前库存' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_待合成库存' AS old_field, 'erp_pending_composite_inventory' AS new_field, 'Excel列名：待合成库存' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_报价币别' AS old_field, 'erp_quotation_currency' AS new_field, 'Excel列名：报价币别' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_报价税率' AS old_field, 'erp_quotation_tax_rate' AS new_field, 'Excel列名：报价税率' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_是否合成物料' AS old_field, 'erp_is_composite_material' AS new_field, 'Excel列名：是否合成物料' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_最大安全库存' AS old_field, 'erp_maximum_safety_inventory' AS new_field, 'Excel列名：最大安全库存' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_最新报价' AS old_field, 'erp_latest_quotation' AS new_field, 'Excel列名：最新报价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_期初库存' AS old_field, 'erp_opening_inventory' AS new_field, 'Excel列名：期初库存' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_材质' AS old_field, 'erp_material' AS new_field, 'Excel列名：材质' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_板厚' AS old_field, 'erp_board_thickness' AS new_field, 'Excel列名：板厚' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_板材型号' AS old_field, 'erp_board_material_model' AS new_field, 'Excel列名：板材型号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_海关编号' AS old_field, 'erp_customs_no' AS new_field, 'Excel列名：海关编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_物料厂牌' AS old_field, 'erp_material_brand' AS new_field, 'Excel列名：物料厂牌' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_物料材质' AS old_field, 'erp_material_material' AS new_field, 'Excel列名：物料材质' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_物料用途' AS old_field, 'erp_material_usage' AS new_field, 'Excel列名：物料用途' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_物料硬度' AS old_field, 'erp_material_hardness' AS new_field, 'Excel列名：物料硬度' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_物料类别' AS old_field, 'erp_material_category' AS new_field, 'Excel列名：物料类别' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_特殊编号' AS old_field, 'erp_special_no' AS new_field, 'Excel列名：特殊编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_生产日期' AS old_field, 'erp_production_date' AS new_field, 'Excel列名：生产日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_目前库存' AS old_field, 'erp_current_inventory' AS new_field, 'Excel列名：目前库存' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_签名' AS old_field, 'erp_signature' AS new_field, 'Excel列名：签名' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_营销模式' AS old_field, 'erp_business_model' AS new_field, 'Excel列名：营销模式' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_规格' AS old_field, 'erp_specification' AS new_field, 'Excel列名：规格' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_财务科目' AS old_field, 'erp_finance_account' AS new_field, 'Excel列名：财务科目' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_资产名称' AS old_field, 'erp_asset_name' AS new_field, 'Excel列名：资产名称' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_资产编号' AS old_field, 'erp_asset_no' AS new_field, 'Excel列名：资产编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_输入日期' AS old_field, 'erp_entry_date' AS new_field, 'Excel列名：输入日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_输入者' AS old_field, 'erp_entered_by' AS new_field, 'Excel列名：输入者' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_铜箔' AS old_field, 'erp_copper_foil' AS new_field, 'Excel列名：铜箔' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_阻燃级别' AS old_field, 'erp_flame_retardant_grade' AS new_field, 'Excel列名：阻燃级别' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material' AS table_name, 'erp_高度' AS old_field, 'erp_height' AS new_field, 'Excel列名：高度' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_A板宽' AS old_field, 'erp_a_board_width' AS new_field, 'Excel列名：A板宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_A板开料块数' AS old_field, 'erp_a_board_cutting_piece_count' AS new_field, 'Excel列名：A板开料块数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_A板长' AS old_field, 'erp_a_board_length' AS new_field, 'Excel列名：A板长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_B板宽' AS old_field, 'erp_b_board_width' AS new_field, 'Excel列名：B板宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_B板开料块数' AS old_field, 'erp_b_board_cutting_piece_count' AS new_field, 'Excel列名：B板开料块数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_B板长' AS old_field, 'erp_b_board_length' AS new_field, 'Excel列名：B板长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_C板宽' AS old_field, 'erp_c_board_width' AS new_field, 'Excel列名：C板宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_C板开料块数' AS old_field, 'erp_c_board_cutting_piece_count' AS new_field, 'Excel列名：C板开料块数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_C板长' AS old_field, 'erp_c_board_length' AS new_field, 'Excel列名：C板长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_D板宽' AS old_field, 'erp_d_board_width' AS new_field, 'Excel列名：D板宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_D板开料块数' AS old_field, 'erp_d_board_cutting_piece_count' AS new_field, 'Excel列名：D板开料块数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_D板长' AS old_field, 'erp_d_board_length' AS new_field, 'Excel列名：D板长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_dind_mc1' AS old_field, 'erp_dind_mc_1' AS new_field, 'Excel列名：dind_mc1' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_dind_mm1' AS old_field, 'erp_dind_mm_1' AS new_field, 'Excel列名：dind_mm1' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_不含税单价' AS old_field, 'erp_tax_exclusive_unit_price' AS new_field, 'Excel列名：不含税单价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_不含税金额(本币)' AS old_field, 'erp_tax_exclusive_amount_local_currency' AS new_field, 'Excel列名：不含税金额(本币)' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_仓位' AS old_field, 'erp_bin' AS new_field, 'Excel列名：仓位' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_仓库名称' AS old_field, 'erp_warehouse_name' AS new_field, 'Excel列名：仓库名称' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_使用部门名称' AS old_field, 'erp_usage_department_name' AS new_field, 'Excel列名：使用部门名称' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_使用部门编号' AS old_field, 'erp_usage_department_no' AS new_field, 'Excel列名：使用部门编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_供应张数' AS old_field, 'erp_supply_sheet_count' AS new_field, 'Excel列名：供应张数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_保质天数' AS old_field, 'erp_shelf_life_days' AS new_field, 'Excel列名：保质天数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_入库单明细ID编号' AS old_field, 'erp_receipt_detail_id_no' AS new_field, 'Excel列名：入库单明细ID编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_入库日期' AS old_field, 'erp_receipt_date' AS new_field, 'Excel列名：入库日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_入库编号' AS old_field, 'erp_receipt_no' AS new_field, 'Excel列名：入库编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_其他mc2' AS old_field, 'erp_mc_2' AS new_field, 'Excel列名：其他mc2' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_其它bc3' AS old_field, 'erp_bc_3' AS new_field, 'Excel列名：其它bc3' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_其它bc4' AS old_field, 'erp_bc_4' AS new_field, 'Excel列名：其它bc4' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_其它bi2' AS old_field, 'erp_bi_2' AS new_field, 'Excel列名：其它bi2' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_其它mb1' AS old_field, 'erp_mb_1' AS new_field, 'Excel列名：其它mb1' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_其它mb2' AS old_field, 'erp_mb_2' AS new_field, 'Excel列名：其它mb2' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_其它mc1' AS old_field, 'erp_mc_1' AS new_field, 'Excel列名：其它mc1' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_其它mm1' AS old_field, 'erp_mm_1' AS new_field, 'Excel列名：其它mm1' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_其它mm2' AS old_field, 'erp_mm_2' AS new_field, 'Excel列名：其它mm2' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_出库单ID' AS old_field, 'erp_material_issue_id' AS new_field, 'Excel列名：出库单ID' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_出库单明细ID' AS old_field, 'erp_material_issue_detail_id' AS new_field, 'Excel列名：出库单明细ID' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_出库类别' AS old_field, 'erp_issue_category' AS new_field, 'Excel列名：出库类别' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_出库重量' AS old_field, 'erp_issue_weight' AS new_field, 'Excel列名：出库重量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_出库面积' AS old_field, 'erp_issue_area' AS new_field, 'Excel列名：出库面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_出货料号' AS old_field, 'erp_shipment_part_no' AS new_field, 'Excel列名：出货料号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_加权单价' AS old_field, 'erp_weighted_unit_price' AS new_field, 'Excel列名：加权单价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_加权单价金额' AS old_field, 'erp_weighted_unit_price_amount' AS new_field, 'Excel列名：加权单价金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_单价' AS old_field, 'erp_unit_price_replenishment_e186288c45' AS new_field, 'Excel列名：单价' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_单价' AS old_field, 'erp_unit_price_source_c958a27931' AS new_field, 'Excel列名：单价' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_单价<本位币>' AS old_field, 'erp_unit_price_local_currency' AS new_field, 'Excel列名：单价<本位币>' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_单位' AS old_field, 'erp_unit_replenishment_26e8962890' AS new_field, 'Excel列名：单位' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_单位' AS old_field, 'erp_unit_source_9659f2994f' AS new_field, 'Excel列名：单位' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_单重' AS old_field, 'erp_unit_weight' AS new_field, 'Excel列名：单重' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_厂内编号' AS old_field, 'erp_internal_product_no_replenishment_9cca17fc3d' AS new_field, 'Excel列名：厂内编号' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_厂内编号' AS old_field, 'erp_internal_product_no_source_18dfd8dc68' AS new_field, 'Excel列名：厂内编号' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_厂商' AS old_field, 'erp_supplier' AS new_field, 'Excel列名：厂商' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_厂商名称' AS old_field, 'erp_supplier_name' AS new_field, 'Excel列名：厂商名称' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_厂商编号' AS old_field, 'erp_supplier_no' AS new_field, 'Excel列名：厂商编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_原下单数量' AS old_field, 'erp_original_order_placed_quantity' AS new_field, 'Excel列名：原下单数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_原客户PO' AS old_field, 'erp_original_customer_po' AS new_field, 'Excel列名：原客户PO' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_原客户交期' AS old_field, 'erp_original_customer_delivery_date' AS new_field, 'Excel列名：原客户交期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_原料大类' AS old_field, 'erp_raw_material_major_category' AS new_field, 'Excel列名：原料大类' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_原料小类' AS old_field, 'erp_raw_material_minor_category' AS new_field, 'Excel列名：原料小类' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_原料编号' AS old_field, 'erp_material_no_source_3b3dc2fa70' AS new_field, 'Excel列名：原料编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_原料编号ID' AS old_field, 'erp_material_no_id' AS new_field, 'Excel列名：原料编号ID' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_原物料名称' AS old_field, 'erp_original_material_name' AS new_field, 'Excel列名：原物料名称' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_原订单编号' AS old_field, 'erp_original_order_no' AS new_field, 'Excel列名：原订单编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_备注' AS old_field, 'erp_remarks' AS new_field, 'Excel列名：备注' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_外包单号' AS old_field, 'erp_subcontract_document_no' AS new_field, 'Excel列名：外包单号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_外包累计领料' AS old_field, 'erp_subcontract_cumulative_material_issue' AS new_field, 'Excel列名：外包累计领料' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_外包表头ID' AS old_field, 'erp_subcontract_header_id' AS new_field, 'Excel列名：外包表头ID' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_外包计划领料' AS old_field, 'erp_subcontract_planned_material_issue' AS new_field, 'Excel列名：外包计划领料' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_大料/边料' AS old_field, 'erp_full_size_material_offcuts' AS new_field, 'Excel列名：大料/边料' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_子类' AS old_field, 'erp_subcategory' AS new_field, 'Excel列名：子类' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_存货类别' AS old_field, 'erp_inventory_category' AS new_field, 'Excel列名：存货类别' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_客户名称' AS old_field, 'erp_customer_name' AS new_field, 'Excel列名：客户名称' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_客户料号' AS old_field, 'erp_customer_part_no_source_00e16c5278' AS new_field, 'Excel列名：客户料号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_客户简称' AS old_field, 'erp_customer_short_name' AS new_field, 'Excel列名：客户简称' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_客户编号' AS old_field, 'erp_customer_code_replenishment_a38c57442a' AS new_field, 'Excel列名：客户编号' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_客户编号' AS old_field, 'erp_customer_code_source_3c7ef4232e' AS new_field, 'Excel列名：客户编号' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_工厂' AS old_field, 'erp_factory' AS new_field, 'Excel列名：工厂' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_工序' AS old_field, 'erp_process' AS new_field, 'Excel列名：工序' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_工序号' AS old_field, 'erp_process_no' AS new_field, 'Excel列名：工序号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_币别' AS old_field, 'erp_currency_replenishment_f8282e9cc3' AS new_field, 'Excel列名：币别' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_币别' AS old_field, 'erp_currency_source_893eac34de' AS new_field, 'Excel列名：币别' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_废品入库' AS old_field, 'erp_scrap_receipt' AS new_field, 'Excel列名：废品入库' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_开料块数' AS old_field, 'erp_cutting_piece_count' AS new_field, 'Excel列名：开料块数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_总投料面积' AS old_field, 'erp_total_material_input_area' AS new_field, 'Excel列名：总投料面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_成本单价' AS old_field, 'erp_cost_unit_price' AS new_field, 'Excel列名：成本单价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_成本金额' AS old_field, 'erp_cost_amount' AS new_field, 'Excel列名：成本金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_投料类别' AS old_field, 'erp_material_input_category' AS new_field, 'Excel列名：投料类别' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_投料面积' AS old_field, 'erp_material_input_area' AS new_field, 'Excel列名：投料面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_料号变更信息' AS old_field, 'erp_part_no_change_information' AS new_field, 'Excel列名：料号变更信息' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_是否固定资产' AS old_field, 'erp_is_fixed_asset' AS new_field, 'Excel列名：是否固定资产' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_最大安全库存' AS old_field, 'erp_maximum_safety_inventory' AS new_field, 'Excel列名：最大安全库存' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_最小安全库存' AS old_field, 'erp_minimum_safety_inventory' AS new_field, 'Excel列名：最小安全库存' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_本位币' AS old_field, 'erp_local_currency' AS new_field, 'Excel列名：本位币' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_本位币金额' AS old_field, 'erp_local_currency_amount' AS new_field, 'Excel列名：本位币金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_本币成本单价' AS old_field, 'erp_local_currency_cost_unit_price' AS new_field, 'Excel列名：本币成本单价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_本币成本金额' AS old_field, 'erp_local_currency_cost_amount' AS new_field, 'Excel列名：本币成本金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_本次领料量' AS old_field, 'erp_current_material_issue_quantity' AS new_field, 'Excel列名：本次领料量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_板材名称' AS old_field, 'erp_board_material_name' AS new_field, 'Excel列名：板材名称' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_板材编号' AS old_field, 'erp_board_material_no' AS new_field, 'Excel列名：板材编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_板材规格' AS old_field, 'erp_board_material_specification' AS new_field, 'Excel列名：板材规格' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_物料编号' AS old_field, 'erp_material_no_source_3d14d54480' AS new_field, 'Excel列名：物料编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_生产bcn5' AS old_field, 'erp_production_bcn_5' AS new_field, 'Excel列名：生产bcn5' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_生产bcn6' AS old_field, 'erp_production_bcn_6' AS new_field, 'Excel列名：生产bcn6' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_生产bcn7' AS old_field, 'erp_production_bcn_7' AS new_field, 'Excel列名：生产bcn7' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_生产bcn8' AS old_field, 'erp_production_bcn_8' AS new_field, 'Excel列名：生产bcn8' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_生产批号' AS old_field, 'erp_production_batch_no' AS new_field, 'Excel列名：生产批号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_生产指令ID' AS old_field, 'erp_production_order_id' AS new_field, 'Excel列名：生产指令ID' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_生产指令号' AS old_field, 'erp_production_order_no' AS new_field, 'Excel列名：生产指令号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_生产日期' AS old_field, 'erp_production_date' AS new_field, 'Excel列名：生产日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_申请部门名称' AS old_field, 'erp_request_department_name' AS new_field, 'Excel列名：申请部门名称' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_申请部门编号' AS old_field, 'erp_request_department_no' AS new_field, 'Excel列名：申请部门编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_盘点月份' AS old_field, 'erp_stocktaking_month' AS new_field, 'Excel列名：盘点月份' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_目前库存' AS old_field, 'erp_current_inventory' AS new_field, 'Excel列名：目前库存' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_税率' AS old_field, 'erp_tax_rate' AS new_field, 'Excel列名：税率' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_累计还入数量' AS old_field, 'erp_cumulative_returned_quantity' AS new_field, 'Excel列名：累计还入数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_累计退仓' AS old_field, 'erp_cumulative_warehouse_return' AS new_field, 'Excel列名：累计退仓' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_累计领料块数' AS old_field, 'erp_cumulative_material_issue_piece_count' AS new_field, 'Excel列名：累计领料块数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_累计领料量' AS old_field, 'erp_cumulative_material_issue_quantity' AS new_field, 'Excel列名：累计领料量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_英文名称' AS old_field, 'erp_english_name' AS new_field, 'Excel列名：英文名称' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_英文规格' AS old_field, 'erp_english_specification' AS new_field, 'Excel列名：英文规格' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_营销模式' AS old_field, 'erp_business_model' AS new_field, 'Excel列名：营销模式' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_补料数量' AS old_field, 'erp_material_replenishment_quantity' AS new_field, 'Excel列名：补料数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_补料日期' AS old_field, 'erp_material_replenishment_date' AS new_field, 'Excel列名：补料日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_补料类型' AS old_field, 'erp_material_replenishment_type' AS new_field, 'Excel列名：补料类型' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_补料面积' AS old_field, 'erp_material_replenishment_area' AS new_field, 'Excel列名：补料面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_要求交期' AS old_field, 'erp_required_delivery_date' AS new_field, 'Excel列名：要求交期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_规格' AS old_field, 'erp_specification' AS new_field, 'Excel列名：规格' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_计划领料块数' AS old_field, 'erp_planned_material_issue_piece_count' AS new_field, 'Excel列名：计划领料块数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_计划领料量' AS old_field, 'erp_planned_material_issue_quantity' AS new_field, 'Excel列名：计划领料量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_订单数量' AS old_field, 'erp_order_quantity' AS new_field, 'Excel列名：订单数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_订单编号' AS old_field, 'erp_order_no' AS new_field, 'Excel列名：订单编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_财务签名' AS old_field, 'erp_finance_signature' AS new_field, 'Excel列名：财务签名' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_财务签名人' AS old_field, 'erp_finance_signature_person' AS new_field, 'Excel列名：财务签名人' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_财务签名日期' AS old_field, 'erp_finance_signature_date' AS new_field, 'Excel列名：财务签名日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_责任部门' AS old_field, 'erp_responsible_department' AS new_field, 'Excel列名：责任部门' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_输入日期' AS old_field, 'erp_entry_date_source_6d3834179d' AS new_field, 'Excel列名：输入日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_输入者' AS old_field, 'erp_entered_by_source_3e8667c782' AS new_field, 'Excel列名：输入者' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_部门' AS old_field, 'erp_department' AS new_field, 'Excel列名：部门' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_金额<本位币>' AS old_field, 'erp_amount_local_currency' AS new_field, 'Excel列名：金额<本位币>' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_领料人' AS old_field, 'erp_material_recipient' AS new_field, 'Excel列名：领料人' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_领料凭证' AS old_field, 'erp_material_issue_voucher' AS new_field, 'Excel列名：领料凭证' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_领料单号' AS old_field, 'erp_material_issue_no' AS new_field, 'Excel列名：领料单号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_领料单号/备注' AS old_field, 'erp_material_issue_no_remarks' AS new_field, 'Excel列名：领料单号/备注' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_领料块数' AS old_field, 'erp_material_issue_piece_count' AS new_field, 'Excel列名：领料块数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_领料日期' AS old_field, 'erp_material_issue_date' AS new_field, 'Excel列名：领料日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_领料申请日期' AS old_field, 'erp_material_issue_request_date' AS new_field, 'Excel列名：领料申请日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_领料申请编号' AS old_field, 'erp_material_issue_request_no' AS new_field, 'Excel列名：领料申请编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_领料目的' AS old_field, 'erp_material_issue_purpose' AS new_field, 'Excel列名：领料目的' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_不含税单价' AS old_field, 'erp_tax_exclusive_unit_price' AS new_field, 'Excel列名：不含税单价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_不含税金额' AS old_field, 'erp_tax_exclusive_amount' AS new_field, 'Excel列名：不含税金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_仓位' AS old_field, 'erp_bin' AS new_field, 'Excel列名：仓位' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_仓库名称' AS old_field, 'erp_warehouse_name' AS new_field, 'Excel列名：仓库名称' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_保质天数' AS old_field, 'erp_shelf_life_days' AS new_field, 'Excel列名：保质天数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_借入部门名称' AS old_field, 'erp_loan_in_department_name' AS new_field, 'Excel列名：借入部门名称' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_借入部门编号' AS old_field, 'erp_loan_in_department_no' AS new_field, 'Excel列名：借入部门编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_借出单号' AS old_field, 'erp_loan_out_document_no' AS new_field, 'Excel列名：借出单号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_停止还出' AS old_field, 'erp_stop_return_out' AS new_field, 'Excel列名：停止还出' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_停止还出人' AS old_field, 'erp_stop_return_out_person' AS new_field, 'Excel列名：停止还出人' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_停止还出备注' AS old_field, 'erp_stop_return_out_remarks' AS new_field, 'Excel列名：停止还出备注' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_停止还出日期' AS old_field, 'erp_stop_return_out_date' AS new_field, 'Excel列名：停止还出日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_停止领料人' AS old_field, 'erp_stop_material_recipient' AS new_field, 'Excel列名：停止领料人' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_停止领料日期' AS old_field, 'erp_stop_material_issue_date' AS new_field, 'Excel列名：停止领料日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_入帐日期' AS old_field, 'erp_posting_date' AS new_field, 'Excel列名：入帐日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_入帐月份' AS old_field, 'erp_posting_month' AS new_field, 'Excel列名：入帐月份' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_入库单号' AS old_field, 'erp_receipt_no' AS new_field, 'Excel列名：入库单号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_入库日期' AS old_field, 'erp_receipt_date' AS new_field, 'Excel列名：入库日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_入库明细编号' AS old_field, 'erp_receipt_detail_no' AS new_field, 'Excel列名：入库明细编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_入库类别' AS old_field, 'erp_receipt_category' AS new_field, 'Excel列名：入库类别' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_入库重量' AS old_field, 'erp_receipt_weight' AS new_field, 'Excel列名：入库重量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_入库面积' AS old_field, 'erp_receipt_area' AS new_field, 'Excel列名：入库面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_其他mc3' AS old_field, 'erp_mc_3' AS new_field, 'Excel列名：其他mc3' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_其他mc4' AS old_field, 'erp_mc_4' AS new_field, 'Excel列名：其他mc4' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_到期日期' AS old_field, 'erp_expiry_date' AS new_field, 'Excel列名：到期日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_单价' AS old_field, 'erp_unit_price' AS new_field, 'Excel列名：单价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_单位' AS old_field, 'erp_unit' AS new_field, 'Excel列名：单位' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_单号' AS old_field, 'erp_document_no' AS new_field, 'Excel列名：单号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_单重' AS old_field, 'erp_unit_weight' AS new_field, 'Excel列名：单重' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_厂商名称' AS old_field, 'erp_supplier_name' AS new_field, 'Excel列名：厂商名称' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_厂商编号' AS old_field, 'erp_supplier_no' AS new_field, 'Excel列名：厂商编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_原料名称' AS old_field, 'erp_material_name' AS new_field, 'Excel列名：原料名称' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_原料大类' AS old_field, 'erp_raw_material_major_category' AS new_field, 'Excel列名：原料大类' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_原料小类' AS old_field, 'erp_raw_material_minor_category' AS new_field, 'Excel列名：原料小类' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_原料编号' AS old_field, 'erp_material_no' AS new_field, 'Excel列名：原料编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_备注' AS old_field, 'erp_remarks' AS new_field, 'Excel列名：备注' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_外发单价' AS old_field, 'erp_outsourcing_unit_price' AS new_field, 'Excel列名：外发单价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_外发厂商名称' AS old_field, 'erp_outsourcing_supplier_name' AS new_field, 'Excel列名：外发厂商名称' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_外发厂商编号' AS old_field, 'erp_outsourcing_supplier_no' AS new_field, 'Excel列名：外发厂商编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_外发币别' AS old_field, 'erp_outsourcing_currency' AS new_field, 'Excel列名：外发币别' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_子类' AS old_field, 'erp_subcategory' AS new_field, 'Excel列名：子类' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_存货类别' AS old_field, 'erp_inventory_category' AS new_field, 'Excel列名：存货类别' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_审核人' AS old_field, 'erp_review_person' AS new_field, 'Excel列名：审核人' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_审核日期' AS old_field, 'erp_review_date' AS new_field, 'Excel列名：审核日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_审核签名' AS old_field, 'erp_review_signature' AS new_field, 'Excel列名：审核签名' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_工厂' AS old_field, 'erp_factory' AS new_field, 'Excel列名：工厂' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_币别' AS old_field, 'erp_currency' AS new_field, 'Excel列名：币别' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_延期天数' AS old_field, 'erp_extension_days' AS new_field, 'Excel列名：延期天数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_成本单价' AS old_field, 'erp_cost_unit_price' AS new_field, 'Excel列名：成本单价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_成本金额' AS old_field, 'erp_cost_amount' AS new_field, 'Excel列名：成本金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_打折' AS old_field, 'erp_discount' AS new_field, 'Excel列名：打折' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_打折单价' AS old_field, 'erp_discount_unit_price' AS new_field, 'Excel列名：打折单价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_扣款' AS old_field, 'erp_deduction' AS new_field, 'Excel列名：扣款' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_报关单号' AS old_field, 'erp_customs_declaration_document_no' AS new_field, 'Excel列名：报关单号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_报关核销' AS old_field, 'erp_customs_writeoff' AS new_field, 'Excel列名：报关核销' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_是否免检' AS old_field, 'erp_is_inspection_exempt' AS new_field, 'Excel列名：是否免检' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_最大安全库存' AS old_field, 'erp_maximum_safety_inventory' AS new_field, 'Excel列名：最大安全库存' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_最小安全库存' AS old_field, 'erp_minimum_safety_inventory' AS new_field, 'Excel列名：最小安全库存' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_有效期' AS old_field, 'erp_valid_until' AS new_field, 'Excel列名：有效期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_本位币金额' AS old_field, 'erp_local_currency_amount' AS new_field, 'Excel列名：本位币金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_本币成本单价' AS old_field, 'erp_local_currency_cost_unit_price' AS new_field, 'Excel列名：本币成本单价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_本币成本金额' AS old_field, 'erp_local_currency_cost_amount' AS new_field, 'Excel列名：本币成本金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_本次入库' AS old_field, 'erp_current_receipt' AS new_field, 'Excel列名：本次入库' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_检验结果' AS old_field, 'erp_inspection_result' AS new_field, 'Excel列名：检验结果' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_生产批号' AS old_field, 'erp_production_batch_no' AS new_field, 'Excel列名：生产批号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_生产日期' AS old_field, 'erp_production_date' AS new_field, 'Excel列名：生产日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_目前库存' AS old_field, 'erp_current_inventory' AS new_field, 'Excel列名：目前库存' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_目前库存金额' AS old_field, 'erp_current_inventory_amount' AS new_field, 'Excel列名：目前库存金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_确认入库数量' AS old_field, 'erp_confirmation_receipt_quantity' AS new_field, 'Excel列名：确认入库数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_确认单价' AS old_field, 'erp_confirmation_unit_price' AS new_field, 'Excel列名：确认单价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_确认数量' AS old_field, 'erp_confirmation_quantity' AS new_field, 'Excel列名：确认数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_确认退货数量' AS old_field, 'erp_confirmation_return_quantity' AS new_field, 'Excel列名：确认退货数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_税率%' AS old_field, 'erp_tax_rate_percent' AS new_field, 'Excel列名：税率%' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_累计交货量' AS old_field, 'erp_cumulative_delivery_quantity' AS new_field, 'Excel列名：累计交货量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_累计还出数量' AS old_field, 'erp_cumulative_return_out_quantity' AS new_field, 'Excel列名：累计还出数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_累计领料' AS old_field, 'erp_cumulative_material_issue' AS new_field, 'Excel列名：累计领料' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_英文名称' AS old_field, 'erp_english_name' AS new_field, 'Excel列名：英文名称' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_英文规格' AS old_field, 'erp_english_specification' AS new_field, 'Excel列名：英文规格' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_营销模式' AS old_field, 'erp_business_model' AS new_field, 'Excel列名：营销模式' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_规格' AS old_field, 'erp_specification' AS new_field, 'Excel列名：规格' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_财务签名' AS old_field, 'erp_finance_signature' AS new_field, 'Excel列名：财务签名' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_财务签名人' AS old_field, 'erp_finance_signature_person' AS new_field, 'Excel列名：财务签名人' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_财务签名日期' AS old_field, 'erp_finance_signature_date' AS new_field, 'Excel列名：财务签名日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_费用类型' AS old_field, 'erp_expense_type' AS new_field, 'Excel列名：费用类型' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_输入日期' AS old_field, 'erp_entry_date' AS new_field, 'Excel列名：输入日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_输入者' AS old_field, 'erp_entered_by' AS new_field, 'Excel列名：输入者' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_退货判定' AS old_field, 'erp_return_determination' AS new_field, 'Excel列名：退货判定' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_退货数量' AS old_field, 'erp_return_quantity' AS new_field, 'Excel列名：退货数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_退货确认' AS old_field, 'erp_return_confirmation' AS new_field, 'Excel列名：退货确认' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_送货单号' AS old_field, 'erp_delivery_note_no' AS new_field, 'Excel列名：送货单号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_部门请购数量' AS old_field, 'erp_department_purchase_requisition_quantity' AS new_field, 'Excel列名：部门请购数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_采购下单日期' AS old_field, 'erp_purchase_order_placed_date' AS new_field, 'Excel列名：采购下单日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_采购单ID' AS old_field, 'erp_purchase_order_id' AS new_field, 'Excel列名：采购单ID' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_采购单号' AS old_field, 'erp_purchase_order_no' AS new_field, 'Excel列名：采购单号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_采购数量' AS old_field, 'erp_purchase_quantity' AS new_field, 'Excel列名：采购数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_额外费用' AS old_field, 'erp_extra_expense' AS new_field, 'Excel列名：额外费用' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_验收单号' AS old_field, 'erp_acceptance_document_no' AS new_field, 'Excel列名：验收单号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_material_receipt' AS table_name, 'erp_验收结果' AS old_field, 'erp_acceptance_result' AS new_field, 'Excel列名：验收结果' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_process_output_summary' AS table_name, 'erp_00:00-04:00' AS old_field, 'erp_time_00_00_04_00' AS new_field, 'Excel列名：00:00-04:00' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_process_output_summary' AS table_name, 'erp_04:00-08:00' AS old_field, 'erp_time_04_00_08_00' AS new_field, 'Excel列名：04:00-08:00' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_process_output_summary' AS table_name, 'erp_10:00-12:00' AS old_field, 'erp_time_10_00_12_00' AS new_field, 'Excel列名：10:00-12:00' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_process_output_summary' AS table_name, 'erp_12:00-15:00' AS old_field, 'erp_time_12_00_15_00' AS new_field, 'Excel列名：12:00-15:00' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_process_output_summary' AS table_name, 'erp_15:00-17:00' AS old_field, 'erp_time_15_00_17_00' AS new_field, 'Excel列名：15:00-17:00' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_process_output_summary' AS table_name, 'erp_17:00-20:00' AS old_field, 'erp_time_17_00_20_00' AS new_field, 'Excel列名：17:00-20:00' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_process_output_summary' AS table_name, 'erp_20:00-22:00' AS old_field, 'erp_time_20_00_22_00' AS new_field, 'Excel列名：20:00-22:00' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_process_output_summary' AS table_name, 'erp_22:00-00:00' AS old_field, 'erp_time_22_00_00_00' AS new_field, 'Excel列名：22:00-00:00' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_process_output_summary' AS table_name, 'erp_8:00-10:00' AS old_field, 'erp_time_8_00_10_00' AS new_field, 'Excel列名：8:00-10:00' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_process_output_summary' AS table_name, 'erp_不良率%' AS old_field, 'erp_defect_rate_percent' AS new_field, 'Excel列名：不良率%' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_process_output_summary' AS table_name, 'erp_不良面积' AS old_field, 'erp_defect_area' AS new_field, 'Excel列名：不良面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_process_output_summary' AS table_name, 'erp_产值目标<平方/日>' AS old_field, 'erp_output_value_target_square_meters_day' AS new_field, 'Excel列名：产值目标 <平方/日>' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_process_output_summary' AS table_name, 'erp_全天累计' AS old_field, 'erp_full_day_cumulative' AS new_field, 'Excel列名：全天累计' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_process_output_summary' AS table_name, 'erp_出勤人数' AS old_field, 'erp_attendance_headcount' AS new_field, 'Excel列名：出勤人数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_process_output_summary' AS table_name, 'erp_出勤总工时' AS old_field, 'erp_attendance_total_labor_hours' AS new_field, 'Excel列名：出勤总工时' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_process_output_summary' AS table_name, 'erp_单双面' AS old_field, 'erp_single_double_sided' AS new_field, 'Excel列名：单双面' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_process_output_summary' AS table_name, 'erp_在线存板平米' AS old_field, 'erp_in_process_board_inventory_square_meters' AS new_field, 'Excel列名：在线存板平米' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_process_output_summary' AS table_name, 'erp_工时效率平米/人/时' AS old_field, 'erp_labor_hours_efficiency_square_meters_person_hour' AS new_field, 'Excel列名：工时效率 平米/人/时' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_process_output_summary' AS table_name, 'erp_工段' AS old_field, 'erp_process_section' AS new_field, 'Excel列名：工段' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_process_output_summary' AS table_name, 'erp_平均耗时' AS old_field, 'erp_average_elapsed_time' AS new_field, 'Excel列名：平均耗时' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_process_output_summary' AS table_name, 'erp_报废率%' AS old_field, 'erp_scrap_rate_percent' AS new_field, 'Excel列名：报废率%' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_process_output_summary' AS table_name, 'erp_报废面积' AS old_field, 'erp_scrap_area' AS new_field, 'Excel列名：报废面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_process_output_summary' AS table_name, 'erp_晚班累计' AS old_field, 'erp_night_shift_cumulative' AS new_field, 'Excel列名：晚班累计' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_process_output_summary' AS table_name, 'erp_款数' AS old_field, 'erp_model_count' AS new_field, 'Excel列名：款数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_process_output_summary' AS table_name, 'erp_款数_全天' AS old_field, 'erp_model_count_full_day' AS new_field, 'Excel列名：款数_全天' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_process_output_summary' AS table_name, 'erp_款数_晚班' AS old_field, 'erp_model_count_night_shift' AS new_field, 'Excel列名：款数_晚班' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_process_output_summary' AS table_name, 'erp_款数_白班' AS old_field, 'erp_model_count_day_shift' AS new_field, 'Excel列名：款数_白班' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_process_output_summary' AS table_name, 'erp_生产面积' AS old_field, 'erp_production_area' AS new_field, 'Excel列名：生产面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_process_output_summary' AS table_name, 'erp_白班累计' AS old_field, 'erp_day_shift_cumulative' AS new_field, 'Excel列名：白班累计' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_process_output_summary' AS table_name, 'erp_线别' AS old_field, 'erp_line' AS new_field, 'Excel列名：线别' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_process_output_summary' AS table_name, 'erp_计件单价<每平方>' AS old_field, 'erp_piecework_unit_price_per_square_meters' AS new_field, 'Excel列名：计件单价 <每平方>' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_process_output_summary' AS table_name, 'erp_计件总额' AS old_field, 'erp_piecework_total_amount' AS new_field, 'Excel列名：计件总额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_process_output_summary' AS table_name, 'erp_达成率%' AS old_field, 'erp_achievement_rate_percent' AS new_field, 'Excel列名：达成率%' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_HUB仓' AS old_field, 'erp_hub_warehouse' AS new_field, 'Excel列名：HUB仓' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_一仓库存' AS old_field, 'erp_warehouse_1_inventory' AS new_field, 'Excel列名：一仓库存' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_三仓库存' AS old_field, 'erp_warehouse_3_inventory' AS new_field, 'Excel列名：三仓库存' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_上次报价单价' AS old_field, 'erp_previous_quotation_unit_price' AS new_field, 'Excel列名：上次报价单价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_上次报价币别' AS old_field, 'erp_previous_quotation_currency' AS new_field, 'Excel列名：上次报价币别' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_上次报价税率' AS old_field, 'erp_previous_quotation_tax_rate' AS new_field, 'Excel列名：上次报价税率' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_不含税金额' AS old_field, 'erp_tax_exclusive_amount' AS new_field, 'Excel列名：不含税金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_不含税金额(本币)' AS old_field, 'erp_tax_exclusive_amount_local_currency' AS new_field, 'Excel列名：不含税金额(本币)' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_主管签名' AS old_field, 'erp_supervisor_signature' AS new_field, 'Excel列名：主管签名' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_主管签名人' AS old_field, 'erp_supervisor_signature_person' AS new_field, 'Excel列名：主管签名人' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_主管签名日期' AS old_field, 'erp_supervisor_signature_date' AS new_field, 'Excel列名：主管签名日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_二仓库存' AS old_field, 'erp_warehouse_2_inventory' AS new_field, 'Excel列名：二仓库存' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_交货ok' AS old_field, 'erp_delivery_ok' AS new_field, 'Excel列名：交货ok' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_交货地址' AS old_field, 'erp_delivery_address' AS new_field, 'Excel列名：交货地址' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_交货日期' AS old_field, 'erp_delivery_date' AS new_field, 'Excel列名：交货日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_付款方式' AS old_field, 'erp_payment_method' AS new_field, 'Excel列名：付款方式' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_停止交货' AS old_field, 'erp_stop_delivery' AS new_field, 'Excel列名：停止交货' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_其他17' AS old_field, 'erp_other_17' AS new_field, 'Excel列名：其他17' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_其他18' AS old_field, 'erp_other_18' AS new_field, 'Excel列名：其他18' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_其他19' AS old_field, 'erp_other_19' AS new_field, 'Excel列名：其他19' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_其他20' AS old_field, 'erp_other_20' AS new_field, 'Excel列名：其他20' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_其他bi1' AS old_field, 'erp_bi_1' AS new_field, 'Excel列名：其他bi1' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_其他mc3' AS old_field, 'erp_mc_3' AS new_field, 'Excel列名：其他mc3' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_其他mc4' AS old_field, 'erp_mc_4' AS new_field, 'Excel列名：其他mc4' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_单价' AS old_field, 'erp_unit_price' AS new_field, 'Excel列名：单价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_单位' AS old_field, 'erp_unit' AS new_field, 'Excel列名：单位' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_厂商' AS old_field, 'erp_supplier' AS new_field, 'Excel列名：厂商' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_厂商全称' AS old_field, 'erp_supplier_full_name' AS new_field, 'Excel列名：厂商全称' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_厂商手机' AS old_field, 'erp_supplier_mobile_phone' AS new_field, 'Excel列名：厂商手机' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_厂商电话' AS old_field, 'erp_supplier_phone' AS new_field, 'Excel列名：厂商电话' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_厂商编号' AS old_field, 'erp_supplier_no' AS new_field, 'Excel列名：厂商编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_厂商联系人' AS old_field, 'erp_supplier_contact_person' AS new_field, 'Excel列名：厂商联系人' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_厂商负责人' AS old_field, 'erp_supplier_responsible_person' AS new_field, 'Excel列名：厂商负责人' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_原料名称' AS old_field, 'erp_material_name' AS new_field, 'Excel列名：原料名称' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_原料大类' AS old_field, 'erp_raw_material_major_category' AS new_field, 'Excel列名：原料大类' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_原料小类' AS old_field, 'erp_raw_material_minor_category' AS new_field, 'Excel列名：原料小类' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_原料编号' AS old_field, 'erp_material_no' AS new_field, 'Excel列名：原料编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_含税类别' AS old_field, 'erp_tax_inclusive_category' AS new_field, 'Excel列名：含税类别' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_四仓库存' AS old_field, 'erp_warehouse_4_inventory' AS new_field, 'Excel列名：四仓库存' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_备注' AS old_field, 'erp_remarks' AS new_field, 'Excel列名：备注' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_审核人' AS old_field, 'erp_review_person' AS new_field, 'Excel列名：审核人' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_审核日期' AS old_field, 'erp_review_date' AS new_field, 'Excel列名：审核日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_工厂' AS old_field, 'erp_factory' AS new_field, 'Excel列名：工厂' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_币别' AS old_field, 'erp_currency' AS new_field, 'Excel列名：币别' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_成本单价' AS old_field, 'erp_cost_unit_price' AS new_field, 'Excel列名：成本单价' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_数量' AS old_field, 'erp_quantity' AS new_field, 'Excel列名：数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_最后一次入库日期' AS old_field, 'erp_last_receipt_date' AS new_field, 'Excel列名：最后一次入库日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_最小包装数' AS old_field, 'erp_minimum_packaging_count' AS new_field, 'Excel列名：最小包装数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_最小采购数' AS old_field, 'erp_minimum_purchase_count' AS new_field, 'Excel列名：最小采购数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_月结天数' AS old_field, 'erp_monthly_settlement_days' AS new_field, 'Excel列名：月结天数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_欠交货量' AS old_field, 'erp_outstanding_delivery_quantity' AS new_field, 'Excel列名：欠交货量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_欠交金额' AS old_field, 'erp_outstanding_delivery_amount' AS new_field, 'Excel列名：欠交金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_目前库存' AS old_field, 'erp_current_inventory' AS new_field, 'Excel列名：目前库存' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_确认交期' AS old_field, 'erp_confirmation_delivery_date' AS new_field, 'Excel列名：确认交期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_确认交期人' AS old_field, 'erp_confirmation_delivery_date_person' AS new_field, 'Excel列名：确认交期人' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_确认交期修改次数' AS old_field, 'erp_confirmation_delivery_date_revision_count' AS new_field, 'Excel列名：确认交期修改次数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_确认交期备注' AS old_field, 'erp_confirmation_delivery_date_remarks' AS new_field, 'Excel列名：确认交期备注' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_确认交期时间' AS old_field, 'erp_confirmation_delivery_date_time' AS new_field, 'Excel列名：确认交期时间' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_税率%' AS old_field, 'erp_tax_rate_percent' AS new_field, 'Excel列名：税率%' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_第一次入库日期' AS old_field, 'erp_first_receipt_date' AS new_field, 'Excel列名：第一次入库日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_签名' AS old_field, 'erp_signature' AS new_field, 'Excel列名：签名' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_签收OK/退单' AS old_field, 'erp_acknowledgement_ok_rejected_order' AS new_field, 'Excel列名：签收OK/退单' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_签收人' AS old_field, 'erp_acknowledgement_person' AS new_field, 'Excel列名：签收人' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_签收日期' AS old_field, 'erp_acknowledgement_date' AS new_field, 'Excel列名：签收日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_累计交货' AS old_field, 'erp_cumulative_delivery' AS new_field, 'Excel列名：累计交货' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_累计预交货数量' AS old_field, 'erp_cumulative_scheduled_delivery_quantity' AS new_field, 'Excel列名：累计预交货数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_英文名称' AS old_field, 'erp_english_name' AS new_field, 'Excel列名：英文名称' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_英文规格' AS old_field, 'erp_english_specification' AS new_field, 'Excel列名：英文规格' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_营销模式' AS old_field, 'erp_business_model' AS new_field, 'Excel列名：营销模式' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_规格' AS old_field, 'erp_specification' AS new_field, 'Excel列名：规格' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_请购单号' AS old_field, 'erp_purchase_requisition_no' AS new_field, 'Excel列名：请购单号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_调价类别' AS old_field, 'erp_price_adjustment_category' AS new_field, 'Excel列名：调价类别' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_输入日期' AS old_field, 'erp_entry_date' AS new_field, 'Excel列名：输入日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_输入者' AS old_field, 'erp_entered_by' AS new_field, 'Excel列名：输入者' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_部门签名' AS old_field, 'erp_department_signature' AS new_field, 'Excel列名：部门签名' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_部门签名人' AS old_field, 'erp_department_signature_person' AS new_field, 'Excel列名：部门签名人' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_部门签名日期' AS old_field, 'erp_department_signature_date' AS new_field, 'Excel列名：部门签名日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_部门请购数量' AS old_field, 'erp_department_purchase_requisition_quantity' AS new_field, 'Excel列名：部门请购数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_采购单号' AS old_field, 'erp_purchase_order_no' AS new_field, 'Excel列名：采购单号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_采购周期' AS old_field, 'erp_purchase_cycle' AS new_field, 'Excel列名：采购周期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_采购日期' AS old_field, 'erp_purchase_date' AS new_field, 'Excel列名：采购日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_采购明细类别' AS old_field, 'erp_purchase_detail_category' AS new_field, 'Excel列名：采购明细类别' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_采购类别' AS old_field, 'erp_purchase_category' AS new_field, 'Excel列名：采购类别' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_采购类别（重复列2）' AS old_field, 'erp_purchase_category_duplicate_2' AS new_field, 'Excel列名：采购类别' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_采购类别（重复列3）' AS old_field, 'erp_purchase_category_duplicate_3' AS new_field, 'Excel列名：采购类别' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_金额' AS old_field, 'erp_amount' AS new_field, 'Excel列名：金额' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_需求日期' AS old_field, 'erp_required_date' AS new_field, 'Excel列名：需求日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_A板宽' AS old_field, 'erp_a_board_width' AS new_field, 'Excel列名：A板宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_A板总PNL' AS old_field, 'erp_a_board_total_pnl' AS new_field, 'Excel列名：A板总PNL' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_A板长' AS old_field, 'erp_a_board_length' AS new_field, 'Excel列名：A板长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_B板宽' AS old_field, 'erp_b_board_width' AS new_field, 'Excel列名：B板宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_B板总PNL' AS old_field, 'erp_b_board_total_pnl' AS new_field, 'Excel列名：B板总PNL' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_B板长' AS old_field, 'erp_b_board_length' AS new_field, 'Excel列名：B板长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_入库/已结批' AS old_field, 'erp_receipt_already_batch_closed' AS new_field, 'Excel列名：入库/已结批' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_厂内编号' AS old_field, 'erp_internal_product_no' AS new_field, 'Excel列名：厂内编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_合拼编号' AS old_field, 'erp_combined_panel_no' AS new_field, 'Excel列名：合拼编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_客户' AS old_field, 'erp_customer' AS new_field, 'Excel列名：客户' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_客户料号' AS old_field, 'erp_customer_part_no' AS new_field, 'Excel列名：客户料号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_层数' AS old_field, 'erp_layer_count' AS new_field, 'Excel列名：层数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_工艺' AS old_field, 'erp_process_technology' AS new_field, 'Excel列名：工艺' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_总WPNL数' AS old_field, 'erp_total_wpnl_count' AS new_field, 'Excel列名：总WPNL数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_总投料面积' AS old_field, 'erp_total_material_input_area' AS new_field, 'Excel列名：总投料面积 ' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_成品利用率' AS old_field, 'erp_finished_goods_utilization_rate' AS new_field, 'Excel列名：成品利用率' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_成型方式' AS old_field, 'erp_forming_method' AS new_field, 'Excel列名：成型方式' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_投单面积<板材>' AS old_field, 'erp_order_input_area_board_material' AS new_field, 'Excel列名：投单面积 <板材>' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_投料数量' AS old_field, 'erp_material_input_quantity' AS new_field, 'Excel列名：投料数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_投料日期' AS old_field, 'erp_material_input_date' AS new_field, 'Excel列名：投料日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_投料正常/异常' AS old_field, 'erp_material_input_normal_abnormal' AS new_field, 'Excel列名：投料正常/异常' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_投料类型' AS old_field, 'erp_material_input_type' AS new_field, 'Excel列名：投料类型' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_报废率%' AS old_field, 'erp_scrap_rate_percent' AS new_field, 'Excel列名：报废率%' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_旧厂内编号' AS old_field, 'erp_old_internal_product_no' AS new_field, 'Excel列名：旧厂内编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_最后入库日期' AS old_field, 'erp_last_receipt_date' AS new_field, 'Excel列名：最后入库日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_未入库数量' AS old_field, 'erp_not_receipt_quantity' AS new_field, 'Excel列名：未入库数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_材质' AS old_field, 'erp_material' AS new_field, 'Excel列名：材质' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_板厚' AS old_field, 'erp_board_thickness' AS new_field, 'Excel列名：板厚' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_板材目前库存' AS old_field, 'erp_board_material_current_inventory' AS new_field, 'Excel列名：板材目前库存' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_板材面积' AS old_field, 'erp_board_material_area' AS new_field, 'Excel列名：板材面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_生产指令号' AS old_field, 'erp_production_order_no' AS new_field, 'Excel列名：生产指令号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_生产通知单数量' AS old_field, 'erp_production_notice_quantity' AS new_field, 'Excel列名：生产通知单数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_累计入库' AS old_field, 'erp_cumulative_receipt' AS new_field, 'Excel列名：累计入库' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_累计报废' AS old_field, 'erp_cumulative_scrap' AS new_field, 'Excel列名：累计报废' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_累计领料' AS old_field, 'erp_cumulative_material_issue' AS new_field, 'Excel列名：累计领料' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_要求交期' AS old_field, 'erp_required_delivery_date' AS new_field, 'Excel列名：要求交期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_计划领料' AS old_field, 'erp_planned_material_issue' AS new_field, 'Excel列名：计划领料' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_订单数量' AS old_field, 'erp_order_quantity' AS new_field, 'Excel列名：订单数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_订单数量（重复列2）' AS old_field, 'erp_order_quantity_duplicate_2' AS new_field, 'Excel列名：订单数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_订单类型' AS old_field, 'erp_order_type' AS new_field, 'Excel列名：订单类型' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_订单编号' AS old_field, 'erp_order_no' AS new_field, 'Excel列名：订单编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_输入日期' AS old_field, 'erp_entry_date' AS new_field, 'Excel列名：输入日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_输入者' AS old_field, 'erp_entered_by' AS new_field, 'Excel列名：输入者' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_连片数' AS old_field, 'erp_array_count' AS new_field, 'Excel列名：连片数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_铜箔' AS old_field, 'erp_copper_foil' AS new_field, 'Excel列名：铜箔' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_预投率' AS old_field, 'erp_planned_material_input_rate' AS new_field, 'Excel列名：预投率' AS comment, 'change' AS migration_kind
) AS m
LEFT JOIN information_schema.columns o ON o.TABLE_SCHEMA = DATABASE() AND o.TABLE_NAME = m.table_name AND o.COLUMN_NAME = m.old_field
LEFT JOIN information_schema.columns n ON n.TABLE_SCHEMA = DATABASE() AND n.TABLE_NAME = m.table_name AND n.COLUMN_NAME = m.new_field
WHERE o.COLUMN_NAME IS NULL OR n.COLUMN_NAME IS NOT NULL OR LOWER(o.COLUMN_TYPE) <> 'longtext'
 OR o.IS_NULLABLE <> 'YES' OR o.COLUMN_DEFAULT IS NOT NULL OR o.EXTRA <> '' OR o.GENERATION_EXPRESSION <> '';

-- Exact source scopes must match the reviewed registry before backfill.
SELECT `tenant_code`, `source_file`, `sheet_name`, COUNT(*) AS row_count FROM `qms_material_issue` GROUP BY `tenant_code`, `source_file`, `sheet_name`;

SET SESSION sql_mode = @erp_migration_saved_sql_mode;
