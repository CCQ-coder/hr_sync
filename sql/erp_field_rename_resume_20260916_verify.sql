-- LIVE RESUME VERIFY 2026-09-16: no contract or deletion is authorized by this file
-- MySQL 5.7+/8.0. Select the intended database before running this file.
-- Use a UTF-8 client. STOP synchronization and take a verified BACKUP first.
-- DDL auto-commits; this is not a transaction or an idempotent rerun script.
SET @erp_migration_saved_sql_mode = @@SESSION.sql_mode;
SET SESSION sql_mode = CONCAT_WS(',', NULLIF(@@SESSION.sql_mode, ''), 'NO_BACKSLASH_ESCAPES');
SET NAMES utf8mb4;

SELECT m.table_name, m.old_field, m.new_field, 'remaining_old_column' AS issue
FROM (
SELECT 'qms_material_issue' AS table_name, 'erp_单价' AS old_field, 'erp_unit_price_replenishment_e186288c45' AS new_field, 'Excel列名：单价' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_单价' AS old_field, 'erp_unit_price_source_c958a27931' AS new_field, 'Excel列名：单价' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_单位' AS old_field, 'erp_unit_replenishment_26e8962890' AS new_field, 'Excel列名：单位' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_单位' AS old_field, 'erp_unit_source_9659f2994f' AS new_field, 'Excel列名：单位' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_厂内编号' AS old_field, 'erp_internal_product_no_replenishment_9cca17fc3d' AS new_field, 'Excel列名：厂内编号' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_厂内编号' AS old_field, 'erp_internal_product_no_source_18dfd8dc68' AS new_field, 'Excel列名：厂内编号' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_客户料号' AS old_field, 'erp_customer_part_no_replenishment_18b2446684' AS new_field, 'Excel列名：客户料号' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_客户料号' AS old_field, 'erp_customer_part_no_source_00e16c5278' AS new_field, 'Excel列名：客户料号' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_客户编号' AS old_field, 'erp_customer_code_replenishment_a38c57442a' AS new_field, 'Excel列名：客户编号' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_客户编号' AS old_field, 'erp_customer_code_source_3c7ef4232e' AS new_field, 'Excel列名：客户编号' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_币别' AS old_field, 'erp_currency_replenishment_f8282e9cc3' AS new_field, 'Excel列名：币别' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_币别' AS old_field, 'erp_currency_source_893eac34de' AS new_field, 'Excel列名：币别' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_输入日期' AS old_field, 'erp_entry_date_replenishment_0b915d259c' AS new_field, 'Excel列名：输入日期' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_输入日期' AS old_field, 'erp_entry_date_source_6d3834179d' AS new_field, 'Excel列名：输入日期' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_输入者' AS old_field, 'erp_entered_by_replenishment_4129200b1d' AS new_field, 'Excel列名：输入者' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_输入者' AS old_field, 'erp_entered_by_source_3e8667c782' AS new_field, 'Excel列名：输入者' AS comment, 'split_source' AS migration_kind
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
SELECT 'qms_purchase_order' AS table_name, 'erp_备货数量' AS old_field, 'erp_stock_preparation_quantity' AS new_field, 'Excel列名：备货数量' AS comment, 'change' AS migration_kind
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
SELECT 'qms_purchase_order' AS table_name, 'erp_换算标准' AS old_field, 'erp_conversion_standard' AS new_field, 'Excel列名：换算标准' AS comment, 'change' AS migration_kind
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
SELECT 'qms_purchase_order' AS table_name, 'erp_标准单位' AS old_field, 'erp_standard_unit' AS new_field, 'Excel列名：标准单位' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_标准单位数量' AS old_field, 'erp_standard_unit_quantity' AS new_field, 'Excel列名：标准单位数量' AS comment, 'change' AS migration_kind
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
SELECT 'qms_purchase_order' AS table_name, 'erp_需采购数量' AS old_field, 'erp_required_purchase_quantity' AS new_field, 'Excel列名：需采购数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_A板宽' AS old_field, 'erp_a_board_width' AS new_field, 'Excel列名：A板宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_A板总PNL' AS old_field, 'erp_a_board_total_pnl' AS new_field, 'Excel列名：A板总PNL' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_A板长' AS old_field, 'erp_a_board_length' AS new_field, 'Excel列名：A板长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_A板面积' AS old_field, 'erp_a_board_area' AS new_field, 'Excel列名：A板面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_B板宽' AS old_field, 'erp_b_board_width' AS new_field, 'Excel列名：B板宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_B板总PNL' AS old_field, 'erp_b_board_total_pnl' AS new_field, 'Excel列名：B板总PNL' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_B板长' AS old_field, 'erp_b_board_length' AS new_field, 'Excel列名：B板长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_B板面积' AS old_field, 'erp_b_board_area' AS new_field, 'Excel列名：B板面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_C板宽' AS old_field, 'erp_c_board_width' AS new_field, 'Excel列名：C板宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_C板总PNL' AS old_field, 'erp_c_board_total_pnl' AS new_field, 'Excel列名：C板总PNL' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_C板长' AS old_field, 'erp_c_board_length' AS new_field, 'Excel列名：C板长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_C板面积' AS old_field, 'erp_c_board_area' AS new_field, 'Excel列名：C板面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_D板宽' AS old_field, 'erp_d_board_width' AS new_field, 'Excel列名：D板宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_D板长' AS old_field, 'erp_d_board_length' AS new_field, 'Excel列名：D板长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_D板面积' AS old_field, 'erp_d_board_area' AS new_field, 'Excel列名：D板面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_MI制作要求1' AS old_field, 'erp_mi_manufacturing_required_1' AS new_field, 'Excel列名：MI制作要求1' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_MI制作要求2' AS old_field, 'erp_mi_manufacturing_required_2' AS new_field, 'Excel列名：MI制作要求2' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_MI制作要求3' AS old_field, 'erp_mi_manufacturing_required_3' AS new_field, 'Excel列名：MI制作要求3' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_PCS宽' AS old_field, 'erp_pcs_width' AS new_field, 'Excel列名：PCS宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_PCS长' AS old_field, 'erp_pcs_length' AS new_field, 'Excel列名：PCS长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_PNL宽' AS old_field, 'erp_pnl_width' AS new_field, 'Excel列名：PNL宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_PNL长' AS old_field, 'erp_pnl_length' AS new_field, 'Excel列名：PNL长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_SET利用率' AS old_field, 'erp_set_utilization_rate' AS new_field, 'Excel列名：SET利用率' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_停止领料' AS old_field, 'erp_stop_material_issue' AS new_field, 'Excel列名：停止领料' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_入库/已结批' AS old_field, 'erp_receipt_already_batch_closed' AS new_field, 'Excel列名：入库/已结批' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_加急订单' AS old_field, 'erp_urgent_order' AS new_field, 'Excel列名：加急订单' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_单PCS面积' AS old_field, 'erp_single_pcs_area' AS new_field, 'Excel列名：单PCS面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_厂内编号' AS old_field, 'erp_internal_product_no' AS new_field, 'Excel列名：厂内编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_合拼厂内编号' AS old_field, 'erp_combined_panel_internal_product_no' AS new_field, 'Excel列名：合拼厂内编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_审核人' AS old_field, 'erp_review_person' AS new_field, 'Excel列名：审核人' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_审核日期' AS old_field, 'erp_review_date' AS new_field, 'Excel列名：审核日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_客户料号' AS old_field, 'erp_customer_part_no' AS new_field, 'Excel列名：客户料号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_客户级别' AS old_field, 'erp_customer_grade' AS new_field, 'Excel列名：客户级别' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_客户编号' AS old_field, 'erp_customer_code' AS new_field, 'Excel列名：客户编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_客户订单' AS old_field, 'erp_customer_order' AS new_field, 'Excel列名：客户订单' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_客户订单面积<成品>' AS old_field, 'erp_customer_order_area_finished_goods' AS new_field, 'Excel列名：客户订单面积 <成品>' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_层数' AS old_field, 'erp_layer_count' AS new_field, 'Excel列名：层数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_工作板利用率' AS old_field, 'erp_panel_utilization_rate' AS new_field, 'Excel列名：工作板利用率' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_工艺' AS old_field, 'erp_process_technology' AS new_field, 'Excel列名：工艺' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_总冲次' AS old_field, 'erp_total_punch_cycles' AS new_field, 'Excel列名：总冲次' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_总印次' AS old_field, 'erp_total_print_cycles' AS new_field, 'Excel列名：总印次' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_总投料面积<成品>' AS old_field, 'erp_total_material_input_area_finished_goods' AS new_field, 'Excel列名：总投料面积 <成品>' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_成品利用率' AS old_field, 'erp_finished_goods_utilization_rate' AS new_field, 'Excel列名：成品利用率' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_成型方式' AS old_field, 'erp_forming_method' AS new_field, 'Excel列名：成型方式' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_打印标记' AS old_field, 'erp_printing_marking' AS new_field, 'Excel列名：打印标记' AS comment, 'change' AS migration_kind
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
SELECT 'qms_work_order' AS table_name, 'erp_损耗‰' AS old_field, 'erp_loss_per_mille' AS new_field, 'Excel列名：损耗‰' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_料号2' AS old_field, 'erp_part_no_2' AS new_field, 'Excel列名：料号2' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_旧厂内编号' AS old_field, 'erp_old_internal_product_no' AS new_field, 'Excel列名：旧厂内编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_最后入库日期' AS old_field, 'erp_last_receipt_date' AS new_field, 'Excel列名：最后入库日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_未入库数量' AS old_field, 'erp_not_receipt_quantity' AS new_field, 'Excel列名：未入库数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_本卡PCS数' AS old_field, 'erp_current_card_pcs_count' AS new_field, 'Excel列名：本卡PCS数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_本卡工作板数' AS old_field, 'erp_current_card_panel_count' AS new_field, 'Excel列名：本卡工作板数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_材质' AS old_field, 'erp_material' AS new_field, 'Excel列名：材质' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_板厚' AS old_field, 'erp_board_thickness' AS new_field, 'Excel列名：板厚' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_板材名称' AS old_field, 'erp_board_material_name' AS new_field, 'Excel列名：板材名称' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_板材目前库存' AS old_field, 'erp_board_material_current_inventory' AS new_field, 'Excel列名：板材目前库存' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_板材编号' AS old_field, 'erp_board_material_no' AS new_field, 'Excel列名：板材编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_板材规格' AS old_field, 'erp_board_material_specification' AS new_field, 'Excel列名：板材规格' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_板材面积' AS old_field, 'erp_board_material_area' AS new_field, 'Excel列名：板材面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_标准用量' AS old_field, 'erp_standard_consumption' AS new_field, 'Excel列名：标准用量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_特殊工艺' AS old_field, 'erp_special_process_technology' AS new_field, 'Excel列名：特殊工艺' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_生产指令号' AS old_field, 'erp_production_order_no' AS new_field, 'Excel列名：生产指令号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_生产通知单号' AS old_field, 'erp_production_notice_no' AS new_field, 'Excel列名：生产通知单号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_生产通知单数量' AS old_field, 'erp_production_notice_quantity' AS new_field, 'Excel列名：生产通知单数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_生产通知单面积<成品>' AS old_field, 'erp_production_notice_area_finished_goods' AS new_field, 'Excel列名：生产通知单面积 <成品>' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_管制卡号' AS old_field, 'erp_control_card_no' AS new_field, 'Excel列名：管制卡号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_累计不良' AS old_field, 'erp_cumulative_defect' AS new_field, 'Excel列名：累计不良' AS comment, 'change' AS migration_kind
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
SELECT 'qms_work_order' AS table_name, 'erp_订单数量<生产通知单>' AS old_field, 'erp_order_quantity_production_notice' AS new_field, 'Excel列名：订单数量 <生产通知单>' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_订单类型' AS old_field, 'erp_order_type' AS new_field, 'Excel列名：订单类型' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_订单编号' AS old_field, 'erp_order_no' AS new_field, 'Excel列名：订单编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_评审交期' AS old_field, 'erp_review_delivery_date' AS new_field, 'Excel列名：评审交期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_输入日期' AS old_field, 'erp_entry_date' AS new_field, 'Excel列名：输入日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_输入者' AS old_field, 'erp_entered_by' AS new_field, 'Excel列名：输入者' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_连片数' AS old_field, 'erp_array_count' AS new_field, 'Excel列名：连片数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_铜箔' AS old_field, 'erp_copper_foil' AS new_field, 'Excel列名：铜箔' AS comment, 'change' AS migration_kind
) AS m JOIN information_schema.columns c ON c.TABLE_SCHEMA=DATABASE() AND c.TABLE_NAME=m.table_name AND c.COLUMN_NAME=m.old_field
WHERE m.migration_kind = 'change'
UNION ALL
SELECT m.table_name, m.old_field, m.new_field, 'missing_new_column' FROM (
SELECT 'qms_material_issue' AS table_name, 'erp_单价' AS old_field, 'erp_unit_price_replenishment_e186288c45' AS new_field, 'Excel列名：单价' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_单价' AS old_field, 'erp_unit_price_source_c958a27931' AS new_field, 'Excel列名：单价' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_单位' AS old_field, 'erp_unit_replenishment_26e8962890' AS new_field, 'Excel列名：单位' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_单位' AS old_field, 'erp_unit_source_9659f2994f' AS new_field, 'Excel列名：单位' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_厂内编号' AS old_field, 'erp_internal_product_no_replenishment_9cca17fc3d' AS new_field, 'Excel列名：厂内编号' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_厂内编号' AS old_field, 'erp_internal_product_no_source_18dfd8dc68' AS new_field, 'Excel列名：厂内编号' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_客户料号' AS old_field, 'erp_customer_part_no_replenishment_18b2446684' AS new_field, 'Excel列名：客户料号' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_客户料号' AS old_field, 'erp_customer_part_no_source_00e16c5278' AS new_field, 'Excel列名：客户料号' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_客户编号' AS old_field, 'erp_customer_code_replenishment_a38c57442a' AS new_field, 'Excel列名：客户编号' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_客户编号' AS old_field, 'erp_customer_code_source_3c7ef4232e' AS new_field, 'Excel列名：客户编号' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_币别' AS old_field, 'erp_currency_replenishment_f8282e9cc3' AS new_field, 'Excel列名：币别' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_币别' AS old_field, 'erp_currency_source_893eac34de' AS new_field, 'Excel列名：币别' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_输入日期' AS old_field, 'erp_entry_date_replenishment_0b915d259c' AS new_field, 'Excel列名：输入日期' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_输入日期' AS old_field, 'erp_entry_date_source_6d3834179d' AS new_field, 'Excel列名：输入日期' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_输入者' AS old_field, 'erp_entered_by_replenishment_4129200b1d' AS new_field, 'Excel列名：输入者' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_输入者' AS old_field, 'erp_entered_by_source_3e8667c782' AS new_field, 'Excel列名：输入者' AS comment, 'split_source' AS migration_kind
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
SELECT 'qms_purchase_order' AS table_name, 'erp_备货数量' AS old_field, 'erp_stock_preparation_quantity' AS new_field, 'Excel列名：备货数量' AS comment, 'change' AS migration_kind
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
SELECT 'qms_purchase_order' AS table_name, 'erp_换算标准' AS old_field, 'erp_conversion_standard' AS new_field, 'Excel列名：换算标准' AS comment, 'change' AS migration_kind
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
SELECT 'qms_purchase_order' AS table_name, 'erp_标准单位' AS old_field, 'erp_standard_unit' AS new_field, 'Excel列名：标准单位' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_标准单位数量' AS old_field, 'erp_standard_unit_quantity' AS new_field, 'Excel列名：标准单位数量' AS comment, 'change' AS migration_kind
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
SELECT 'qms_purchase_order' AS table_name, 'erp_需采购数量' AS old_field, 'erp_required_purchase_quantity' AS new_field, 'Excel列名：需采购数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_A板宽' AS old_field, 'erp_a_board_width' AS new_field, 'Excel列名：A板宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_A板总PNL' AS old_field, 'erp_a_board_total_pnl' AS new_field, 'Excel列名：A板总PNL' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_A板长' AS old_field, 'erp_a_board_length' AS new_field, 'Excel列名：A板长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_A板面积' AS old_field, 'erp_a_board_area' AS new_field, 'Excel列名：A板面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_B板宽' AS old_field, 'erp_b_board_width' AS new_field, 'Excel列名：B板宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_B板总PNL' AS old_field, 'erp_b_board_total_pnl' AS new_field, 'Excel列名：B板总PNL' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_B板长' AS old_field, 'erp_b_board_length' AS new_field, 'Excel列名：B板长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_B板面积' AS old_field, 'erp_b_board_area' AS new_field, 'Excel列名：B板面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_C板宽' AS old_field, 'erp_c_board_width' AS new_field, 'Excel列名：C板宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_C板总PNL' AS old_field, 'erp_c_board_total_pnl' AS new_field, 'Excel列名：C板总PNL' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_C板长' AS old_field, 'erp_c_board_length' AS new_field, 'Excel列名：C板长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_C板面积' AS old_field, 'erp_c_board_area' AS new_field, 'Excel列名：C板面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_D板宽' AS old_field, 'erp_d_board_width' AS new_field, 'Excel列名：D板宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_D板长' AS old_field, 'erp_d_board_length' AS new_field, 'Excel列名：D板长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_D板面积' AS old_field, 'erp_d_board_area' AS new_field, 'Excel列名：D板面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_MI制作要求1' AS old_field, 'erp_mi_manufacturing_required_1' AS new_field, 'Excel列名：MI制作要求1' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_MI制作要求2' AS old_field, 'erp_mi_manufacturing_required_2' AS new_field, 'Excel列名：MI制作要求2' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_MI制作要求3' AS old_field, 'erp_mi_manufacturing_required_3' AS new_field, 'Excel列名：MI制作要求3' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_PCS宽' AS old_field, 'erp_pcs_width' AS new_field, 'Excel列名：PCS宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_PCS长' AS old_field, 'erp_pcs_length' AS new_field, 'Excel列名：PCS长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_PNL宽' AS old_field, 'erp_pnl_width' AS new_field, 'Excel列名：PNL宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_PNL长' AS old_field, 'erp_pnl_length' AS new_field, 'Excel列名：PNL长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_SET利用率' AS old_field, 'erp_set_utilization_rate' AS new_field, 'Excel列名：SET利用率' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_停止领料' AS old_field, 'erp_stop_material_issue' AS new_field, 'Excel列名：停止领料' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_入库/已结批' AS old_field, 'erp_receipt_already_batch_closed' AS new_field, 'Excel列名：入库/已结批' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_加急订单' AS old_field, 'erp_urgent_order' AS new_field, 'Excel列名：加急订单' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_单PCS面积' AS old_field, 'erp_single_pcs_area' AS new_field, 'Excel列名：单PCS面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_厂内编号' AS old_field, 'erp_internal_product_no' AS new_field, 'Excel列名：厂内编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_合拼厂内编号' AS old_field, 'erp_combined_panel_internal_product_no' AS new_field, 'Excel列名：合拼厂内编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_审核人' AS old_field, 'erp_review_person' AS new_field, 'Excel列名：审核人' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_审核日期' AS old_field, 'erp_review_date' AS new_field, 'Excel列名：审核日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_客户料号' AS old_field, 'erp_customer_part_no' AS new_field, 'Excel列名：客户料号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_客户级别' AS old_field, 'erp_customer_grade' AS new_field, 'Excel列名：客户级别' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_客户编号' AS old_field, 'erp_customer_code' AS new_field, 'Excel列名：客户编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_客户订单' AS old_field, 'erp_customer_order' AS new_field, 'Excel列名：客户订单' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_客户订单面积<成品>' AS old_field, 'erp_customer_order_area_finished_goods' AS new_field, 'Excel列名：客户订单面积 <成品>' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_层数' AS old_field, 'erp_layer_count' AS new_field, 'Excel列名：层数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_工作板利用率' AS old_field, 'erp_panel_utilization_rate' AS new_field, 'Excel列名：工作板利用率' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_工艺' AS old_field, 'erp_process_technology' AS new_field, 'Excel列名：工艺' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_总冲次' AS old_field, 'erp_total_punch_cycles' AS new_field, 'Excel列名：总冲次' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_总印次' AS old_field, 'erp_total_print_cycles' AS new_field, 'Excel列名：总印次' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_总投料面积<成品>' AS old_field, 'erp_total_material_input_area_finished_goods' AS new_field, 'Excel列名：总投料面积 <成品>' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_成品利用率' AS old_field, 'erp_finished_goods_utilization_rate' AS new_field, 'Excel列名：成品利用率' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_成型方式' AS old_field, 'erp_forming_method' AS new_field, 'Excel列名：成型方式' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_打印标记' AS old_field, 'erp_printing_marking' AS new_field, 'Excel列名：打印标记' AS comment, 'change' AS migration_kind
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
SELECT 'qms_work_order' AS table_name, 'erp_损耗‰' AS old_field, 'erp_loss_per_mille' AS new_field, 'Excel列名：损耗‰' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_料号2' AS old_field, 'erp_part_no_2' AS new_field, 'Excel列名：料号2' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_旧厂内编号' AS old_field, 'erp_old_internal_product_no' AS new_field, 'Excel列名：旧厂内编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_最后入库日期' AS old_field, 'erp_last_receipt_date' AS new_field, 'Excel列名：最后入库日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_未入库数量' AS old_field, 'erp_not_receipt_quantity' AS new_field, 'Excel列名：未入库数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_本卡PCS数' AS old_field, 'erp_current_card_pcs_count' AS new_field, 'Excel列名：本卡PCS数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_本卡工作板数' AS old_field, 'erp_current_card_panel_count' AS new_field, 'Excel列名：本卡工作板数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_材质' AS old_field, 'erp_material' AS new_field, 'Excel列名：材质' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_板厚' AS old_field, 'erp_board_thickness' AS new_field, 'Excel列名：板厚' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_板材名称' AS old_field, 'erp_board_material_name' AS new_field, 'Excel列名：板材名称' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_板材目前库存' AS old_field, 'erp_board_material_current_inventory' AS new_field, 'Excel列名：板材目前库存' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_板材编号' AS old_field, 'erp_board_material_no' AS new_field, 'Excel列名：板材编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_板材规格' AS old_field, 'erp_board_material_specification' AS new_field, 'Excel列名：板材规格' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_板材面积' AS old_field, 'erp_board_material_area' AS new_field, 'Excel列名：板材面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_标准用量' AS old_field, 'erp_standard_consumption' AS new_field, 'Excel列名：标准用量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_特殊工艺' AS old_field, 'erp_special_process_technology' AS new_field, 'Excel列名：特殊工艺' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_生产指令号' AS old_field, 'erp_production_order_no' AS new_field, 'Excel列名：生产指令号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_生产通知单号' AS old_field, 'erp_production_notice_no' AS new_field, 'Excel列名：生产通知单号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_生产通知单数量' AS old_field, 'erp_production_notice_quantity' AS new_field, 'Excel列名：生产通知单数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_生产通知单面积<成品>' AS old_field, 'erp_production_notice_area_finished_goods' AS new_field, 'Excel列名：生产通知单面积 <成品>' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_管制卡号' AS old_field, 'erp_control_card_no' AS new_field, 'Excel列名：管制卡号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_累计不良' AS old_field, 'erp_cumulative_defect' AS new_field, 'Excel列名：累计不良' AS comment, 'change' AS migration_kind
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
SELECT 'qms_work_order' AS table_name, 'erp_订单数量<生产通知单>' AS old_field, 'erp_order_quantity_production_notice' AS new_field, 'Excel列名：订单数量 <生产通知单>' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_订单类型' AS old_field, 'erp_order_type' AS new_field, 'Excel列名：订单类型' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_订单编号' AS old_field, 'erp_order_no' AS new_field, 'Excel列名：订单编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_评审交期' AS old_field, 'erp_review_delivery_date' AS new_field, 'Excel列名：评审交期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_输入日期' AS old_field, 'erp_entry_date' AS new_field, 'Excel列名：输入日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_输入者' AS old_field, 'erp_entered_by' AS new_field, 'Excel列名：输入者' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_连片数' AS old_field, 'erp_array_count' AS new_field, 'Excel列名：连片数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_铜箔' AS old_field, 'erp_copper_foil' AS new_field, 'Excel列名：铜箔' AS comment, 'change' AS migration_kind
) AS m
LEFT JOIN information_schema.columns c ON c.TABLE_SCHEMA=DATABASE() AND c.TABLE_NAME=m.table_name AND c.COLUMN_NAME=m.new_field WHERE c.COLUMN_NAME IS NULL
UNION ALL
SELECT m.table_name, m.old_field, m.new_field, 'comment_mismatch' FROM (
SELECT 'qms_material_issue' AS table_name, 'erp_单价' AS old_field, 'erp_unit_price_replenishment_e186288c45' AS new_field, 'Excel列名：单价' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_单价' AS old_field, 'erp_unit_price_source_c958a27931' AS new_field, 'Excel列名：单价' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_单位' AS old_field, 'erp_unit_replenishment_26e8962890' AS new_field, 'Excel列名：单位' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_单位' AS old_field, 'erp_unit_source_9659f2994f' AS new_field, 'Excel列名：单位' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_厂内编号' AS old_field, 'erp_internal_product_no_replenishment_9cca17fc3d' AS new_field, 'Excel列名：厂内编号' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_厂内编号' AS old_field, 'erp_internal_product_no_source_18dfd8dc68' AS new_field, 'Excel列名：厂内编号' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_客户料号' AS old_field, 'erp_customer_part_no_replenishment_18b2446684' AS new_field, 'Excel列名：客户料号' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_客户料号' AS old_field, 'erp_customer_part_no_source_00e16c5278' AS new_field, 'Excel列名：客户料号' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_客户编号' AS old_field, 'erp_customer_code_replenishment_a38c57442a' AS new_field, 'Excel列名：客户编号' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_客户编号' AS old_field, 'erp_customer_code_source_3c7ef4232e' AS new_field, 'Excel列名：客户编号' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_币别' AS old_field, 'erp_currency_replenishment_f8282e9cc3' AS new_field, 'Excel列名：币别' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_币别' AS old_field, 'erp_currency_source_893eac34de' AS new_field, 'Excel列名：币别' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_输入日期' AS old_field, 'erp_entry_date_replenishment_0b915d259c' AS new_field, 'Excel列名：输入日期' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_输入日期' AS old_field, 'erp_entry_date_source_6d3834179d' AS new_field, 'Excel列名：输入日期' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_输入者' AS old_field, 'erp_entered_by_replenishment_4129200b1d' AS new_field, 'Excel列名：输入者' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_输入者' AS old_field, 'erp_entered_by_source_3e8667c782' AS new_field, 'Excel列名：输入者' AS comment, 'split_source' AS migration_kind
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
SELECT 'qms_purchase_order' AS table_name, 'erp_备货数量' AS old_field, 'erp_stock_preparation_quantity' AS new_field, 'Excel列名：备货数量' AS comment, 'change' AS migration_kind
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
SELECT 'qms_purchase_order' AS table_name, 'erp_换算标准' AS old_field, 'erp_conversion_standard' AS new_field, 'Excel列名：换算标准' AS comment, 'change' AS migration_kind
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
SELECT 'qms_purchase_order' AS table_name, 'erp_标准单位' AS old_field, 'erp_standard_unit' AS new_field, 'Excel列名：标准单位' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_标准单位数量' AS old_field, 'erp_standard_unit_quantity' AS new_field, 'Excel列名：标准单位数量' AS comment, 'change' AS migration_kind
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
SELECT 'qms_purchase_order' AS table_name, 'erp_需采购数量' AS old_field, 'erp_required_purchase_quantity' AS new_field, 'Excel列名：需采购数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_A板宽' AS old_field, 'erp_a_board_width' AS new_field, 'Excel列名：A板宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_A板总PNL' AS old_field, 'erp_a_board_total_pnl' AS new_field, 'Excel列名：A板总PNL' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_A板长' AS old_field, 'erp_a_board_length' AS new_field, 'Excel列名：A板长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_A板面积' AS old_field, 'erp_a_board_area' AS new_field, 'Excel列名：A板面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_B板宽' AS old_field, 'erp_b_board_width' AS new_field, 'Excel列名：B板宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_B板总PNL' AS old_field, 'erp_b_board_total_pnl' AS new_field, 'Excel列名：B板总PNL' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_B板长' AS old_field, 'erp_b_board_length' AS new_field, 'Excel列名：B板长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_B板面积' AS old_field, 'erp_b_board_area' AS new_field, 'Excel列名：B板面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_C板宽' AS old_field, 'erp_c_board_width' AS new_field, 'Excel列名：C板宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_C板总PNL' AS old_field, 'erp_c_board_total_pnl' AS new_field, 'Excel列名：C板总PNL' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_C板长' AS old_field, 'erp_c_board_length' AS new_field, 'Excel列名：C板长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_C板面积' AS old_field, 'erp_c_board_area' AS new_field, 'Excel列名：C板面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_D板宽' AS old_field, 'erp_d_board_width' AS new_field, 'Excel列名：D板宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_D板长' AS old_field, 'erp_d_board_length' AS new_field, 'Excel列名：D板长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_D板面积' AS old_field, 'erp_d_board_area' AS new_field, 'Excel列名：D板面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_MI制作要求1' AS old_field, 'erp_mi_manufacturing_required_1' AS new_field, 'Excel列名：MI制作要求1' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_MI制作要求2' AS old_field, 'erp_mi_manufacturing_required_2' AS new_field, 'Excel列名：MI制作要求2' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_MI制作要求3' AS old_field, 'erp_mi_manufacturing_required_3' AS new_field, 'Excel列名：MI制作要求3' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_PCS宽' AS old_field, 'erp_pcs_width' AS new_field, 'Excel列名：PCS宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_PCS长' AS old_field, 'erp_pcs_length' AS new_field, 'Excel列名：PCS长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_PNL宽' AS old_field, 'erp_pnl_width' AS new_field, 'Excel列名：PNL宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_PNL长' AS old_field, 'erp_pnl_length' AS new_field, 'Excel列名：PNL长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_SET利用率' AS old_field, 'erp_set_utilization_rate' AS new_field, 'Excel列名：SET利用率' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_停止领料' AS old_field, 'erp_stop_material_issue' AS new_field, 'Excel列名：停止领料' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_入库/已结批' AS old_field, 'erp_receipt_already_batch_closed' AS new_field, 'Excel列名：入库/已结批' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_加急订单' AS old_field, 'erp_urgent_order' AS new_field, 'Excel列名：加急订单' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_单PCS面积' AS old_field, 'erp_single_pcs_area' AS new_field, 'Excel列名：单PCS面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_厂内编号' AS old_field, 'erp_internal_product_no' AS new_field, 'Excel列名：厂内编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_合拼厂内编号' AS old_field, 'erp_combined_panel_internal_product_no' AS new_field, 'Excel列名：合拼厂内编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_审核人' AS old_field, 'erp_review_person' AS new_field, 'Excel列名：审核人' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_审核日期' AS old_field, 'erp_review_date' AS new_field, 'Excel列名：审核日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_客户料号' AS old_field, 'erp_customer_part_no' AS new_field, 'Excel列名：客户料号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_客户级别' AS old_field, 'erp_customer_grade' AS new_field, 'Excel列名：客户级别' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_客户编号' AS old_field, 'erp_customer_code' AS new_field, 'Excel列名：客户编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_客户订单' AS old_field, 'erp_customer_order' AS new_field, 'Excel列名：客户订单' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_客户订单面积<成品>' AS old_field, 'erp_customer_order_area_finished_goods' AS new_field, 'Excel列名：客户订单面积 <成品>' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_层数' AS old_field, 'erp_layer_count' AS new_field, 'Excel列名：层数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_工作板利用率' AS old_field, 'erp_panel_utilization_rate' AS new_field, 'Excel列名：工作板利用率' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_工艺' AS old_field, 'erp_process_technology' AS new_field, 'Excel列名：工艺' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_总冲次' AS old_field, 'erp_total_punch_cycles' AS new_field, 'Excel列名：总冲次' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_总印次' AS old_field, 'erp_total_print_cycles' AS new_field, 'Excel列名：总印次' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_总投料面积<成品>' AS old_field, 'erp_total_material_input_area_finished_goods' AS new_field, 'Excel列名：总投料面积 <成品>' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_成品利用率' AS old_field, 'erp_finished_goods_utilization_rate' AS new_field, 'Excel列名：成品利用率' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_成型方式' AS old_field, 'erp_forming_method' AS new_field, 'Excel列名：成型方式' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_打印标记' AS old_field, 'erp_printing_marking' AS new_field, 'Excel列名：打印标记' AS comment, 'change' AS migration_kind
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
SELECT 'qms_work_order' AS table_name, 'erp_损耗‰' AS old_field, 'erp_loss_per_mille' AS new_field, 'Excel列名：损耗‰' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_料号2' AS old_field, 'erp_part_no_2' AS new_field, 'Excel列名：料号2' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_旧厂内编号' AS old_field, 'erp_old_internal_product_no' AS new_field, 'Excel列名：旧厂内编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_最后入库日期' AS old_field, 'erp_last_receipt_date' AS new_field, 'Excel列名：最后入库日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_未入库数量' AS old_field, 'erp_not_receipt_quantity' AS new_field, 'Excel列名：未入库数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_本卡PCS数' AS old_field, 'erp_current_card_pcs_count' AS new_field, 'Excel列名：本卡PCS数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_本卡工作板数' AS old_field, 'erp_current_card_panel_count' AS new_field, 'Excel列名：本卡工作板数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_材质' AS old_field, 'erp_material' AS new_field, 'Excel列名：材质' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_板厚' AS old_field, 'erp_board_thickness' AS new_field, 'Excel列名：板厚' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_板材名称' AS old_field, 'erp_board_material_name' AS new_field, 'Excel列名：板材名称' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_板材目前库存' AS old_field, 'erp_board_material_current_inventory' AS new_field, 'Excel列名：板材目前库存' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_板材编号' AS old_field, 'erp_board_material_no' AS new_field, 'Excel列名：板材编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_板材规格' AS old_field, 'erp_board_material_specification' AS new_field, 'Excel列名：板材规格' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_板材面积' AS old_field, 'erp_board_material_area' AS new_field, 'Excel列名：板材面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_标准用量' AS old_field, 'erp_standard_consumption' AS new_field, 'Excel列名：标准用量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_特殊工艺' AS old_field, 'erp_special_process_technology' AS new_field, 'Excel列名：特殊工艺' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_生产指令号' AS old_field, 'erp_production_order_no' AS new_field, 'Excel列名：生产指令号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_生产通知单号' AS old_field, 'erp_production_notice_no' AS new_field, 'Excel列名：生产通知单号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_生产通知单数量' AS old_field, 'erp_production_notice_quantity' AS new_field, 'Excel列名：生产通知单数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_生产通知单面积<成品>' AS old_field, 'erp_production_notice_area_finished_goods' AS new_field, 'Excel列名：生产通知单面积 <成品>' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_管制卡号' AS old_field, 'erp_control_card_no' AS new_field, 'Excel列名：管制卡号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_累计不良' AS old_field, 'erp_cumulative_defect' AS new_field, 'Excel列名：累计不良' AS comment, 'change' AS migration_kind
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
SELECT 'qms_work_order' AS table_name, 'erp_订单数量<生产通知单>' AS old_field, 'erp_order_quantity_production_notice' AS new_field, 'Excel列名：订单数量 <生产通知单>' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_订单类型' AS old_field, 'erp_order_type' AS new_field, 'Excel列名：订单类型' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_订单编号' AS old_field, 'erp_order_no' AS new_field, 'Excel列名：订单编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_评审交期' AS old_field, 'erp_review_delivery_date' AS new_field, 'Excel列名：评审交期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_输入日期' AS old_field, 'erp_entry_date' AS new_field, 'Excel列名：输入日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_输入者' AS old_field, 'erp_entered_by' AS new_field, 'Excel列名：输入者' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_连片数' AS old_field, 'erp_array_count' AS new_field, 'Excel列名：连片数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_铜箔' AS old_field, 'erp_copper_foil' AS new_field, 'Excel列名：铜箔' AS comment, 'change' AS migration_kind
) AS m
JOIN information_schema.columns c ON c.TABLE_SCHEMA=DATABASE() AND c.TABLE_NAME=m.table_name AND c.COLUMN_NAME=m.new_field WHERE BINARY c.COLUMN_COMMENT <> BINARY m.comment
UNION ALL
SELECT m.table_name, m.old_field, m.new_field, 'definition_mismatch' FROM (
SELECT 'qms_material_issue' AS table_name, 'erp_单价' AS old_field, 'erp_unit_price_replenishment_e186288c45' AS new_field, 'Excel列名：单价' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_单价' AS old_field, 'erp_unit_price_source_c958a27931' AS new_field, 'Excel列名：单价' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_单位' AS old_field, 'erp_unit_replenishment_26e8962890' AS new_field, 'Excel列名：单位' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_单位' AS old_field, 'erp_unit_source_9659f2994f' AS new_field, 'Excel列名：单位' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_厂内编号' AS old_field, 'erp_internal_product_no_replenishment_9cca17fc3d' AS new_field, 'Excel列名：厂内编号' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_厂内编号' AS old_field, 'erp_internal_product_no_source_18dfd8dc68' AS new_field, 'Excel列名：厂内编号' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_客户料号' AS old_field, 'erp_customer_part_no_replenishment_18b2446684' AS new_field, 'Excel列名：客户料号' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_客户料号' AS old_field, 'erp_customer_part_no_source_00e16c5278' AS new_field, 'Excel列名：客户料号' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_客户编号' AS old_field, 'erp_customer_code_replenishment_a38c57442a' AS new_field, 'Excel列名：客户编号' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_客户编号' AS old_field, 'erp_customer_code_source_3c7ef4232e' AS new_field, 'Excel列名：客户编号' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_币别' AS old_field, 'erp_currency_replenishment_f8282e9cc3' AS new_field, 'Excel列名：币别' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_币别' AS old_field, 'erp_currency_source_893eac34de' AS new_field, 'Excel列名：币别' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_输入日期' AS old_field, 'erp_entry_date_replenishment_0b915d259c' AS new_field, 'Excel列名：输入日期' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_输入日期' AS old_field, 'erp_entry_date_source_6d3834179d' AS new_field, 'Excel列名：输入日期' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_输入者' AS old_field, 'erp_entered_by_replenishment_4129200b1d' AS new_field, 'Excel列名：输入者' AS comment, 'split_source' AS migration_kind
UNION ALL
SELECT 'qms_material_issue' AS table_name, 'erp_输入者' AS old_field, 'erp_entered_by_source_3e8667c782' AS new_field, 'Excel列名：输入者' AS comment, 'split_source' AS migration_kind
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
SELECT 'qms_purchase_order' AS table_name, 'erp_备货数量' AS old_field, 'erp_stock_preparation_quantity' AS new_field, 'Excel列名：备货数量' AS comment, 'change' AS migration_kind
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
SELECT 'qms_purchase_order' AS table_name, 'erp_换算标准' AS old_field, 'erp_conversion_standard' AS new_field, 'Excel列名：换算标准' AS comment, 'change' AS migration_kind
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
SELECT 'qms_purchase_order' AS table_name, 'erp_标准单位' AS old_field, 'erp_standard_unit' AS new_field, 'Excel列名：标准单位' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_purchase_order' AS table_name, 'erp_标准单位数量' AS old_field, 'erp_standard_unit_quantity' AS new_field, 'Excel列名：标准单位数量' AS comment, 'change' AS migration_kind
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
SELECT 'qms_purchase_order' AS table_name, 'erp_需采购数量' AS old_field, 'erp_required_purchase_quantity' AS new_field, 'Excel列名：需采购数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_A板宽' AS old_field, 'erp_a_board_width' AS new_field, 'Excel列名：A板宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_A板总PNL' AS old_field, 'erp_a_board_total_pnl' AS new_field, 'Excel列名：A板总PNL' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_A板长' AS old_field, 'erp_a_board_length' AS new_field, 'Excel列名：A板长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_A板面积' AS old_field, 'erp_a_board_area' AS new_field, 'Excel列名：A板面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_B板宽' AS old_field, 'erp_b_board_width' AS new_field, 'Excel列名：B板宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_B板总PNL' AS old_field, 'erp_b_board_total_pnl' AS new_field, 'Excel列名：B板总PNL' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_B板长' AS old_field, 'erp_b_board_length' AS new_field, 'Excel列名：B板长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_B板面积' AS old_field, 'erp_b_board_area' AS new_field, 'Excel列名：B板面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_C板宽' AS old_field, 'erp_c_board_width' AS new_field, 'Excel列名：C板宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_C板总PNL' AS old_field, 'erp_c_board_total_pnl' AS new_field, 'Excel列名：C板总PNL' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_C板长' AS old_field, 'erp_c_board_length' AS new_field, 'Excel列名：C板长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_C板面积' AS old_field, 'erp_c_board_area' AS new_field, 'Excel列名：C板面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_D板宽' AS old_field, 'erp_d_board_width' AS new_field, 'Excel列名：D板宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_D板长' AS old_field, 'erp_d_board_length' AS new_field, 'Excel列名：D板长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_D板面积' AS old_field, 'erp_d_board_area' AS new_field, 'Excel列名：D板面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_MI制作要求1' AS old_field, 'erp_mi_manufacturing_required_1' AS new_field, 'Excel列名：MI制作要求1' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_MI制作要求2' AS old_field, 'erp_mi_manufacturing_required_2' AS new_field, 'Excel列名：MI制作要求2' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_MI制作要求3' AS old_field, 'erp_mi_manufacturing_required_3' AS new_field, 'Excel列名：MI制作要求3' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_PCS宽' AS old_field, 'erp_pcs_width' AS new_field, 'Excel列名：PCS宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_PCS长' AS old_field, 'erp_pcs_length' AS new_field, 'Excel列名：PCS长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_PNL宽' AS old_field, 'erp_pnl_width' AS new_field, 'Excel列名：PNL宽' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_PNL长' AS old_field, 'erp_pnl_length' AS new_field, 'Excel列名：PNL长' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_SET利用率' AS old_field, 'erp_set_utilization_rate' AS new_field, 'Excel列名：SET利用率' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_停止领料' AS old_field, 'erp_stop_material_issue' AS new_field, 'Excel列名：停止领料' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_入库/已结批' AS old_field, 'erp_receipt_already_batch_closed' AS new_field, 'Excel列名：入库/已结批' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_加急订单' AS old_field, 'erp_urgent_order' AS new_field, 'Excel列名：加急订单' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_单PCS面积' AS old_field, 'erp_single_pcs_area' AS new_field, 'Excel列名：单PCS面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_厂内编号' AS old_field, 'erp_internal_product_no' AS new_field, 'Excel列名：厂内编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_合拼厂内编号' AS old_field, 'erp_combined_panel_internal_product_no' AS new_field, 'Excel列名：合拼厂内编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_审核人' AS old_field, 'erp_review_person' AS new_field, 'Excel列名：审核人' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_审核日期' AS old_field, 'erp_review_date' AS new_field, 'Excel列名：审核日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_客户料号' AS old_field, 'erp_customer_part_no' AS new_field, 'Excel列名：客户料号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_客户级别' AS old_field, 'erp_customer_grade' AS new_field, 'Excel列名：客户级别' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_客户编号' AS old_field, 'erp_customer_code' AS new_field, 'Excel列名：客户编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_客户订单' AS old_field, 'erp_customer_order' AS new_field, 'Excel列名：客户订单' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_客户订单面积<成品>' AS old_field, 'erp_customer_order_area_finished_goods' AS new_field, 'Excel列名：客户订单面积 <成品>' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_层数' AS old_field, 'erp_layer_count' AS new_field, 'Excel列名：层数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_工作板利用率' AS old_field, 'erp_panel_utilization_rate' AS new_field, 'Excel列名：工作板利用率' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_工艺' AS old_field, 'erp_process_technology' AS new_field, 'Excel列名：工艺' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_总冲次' AS old_field, 'erp_total_punch_cycles' AS new_field, 'Excel列名：总冲次' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_总印次' AS old_field, 'erp_total_print_cycles' AS new_field, 'Excel列名：总印次' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_总投料面积<成品>' AS old_field, 'erp_total_material_input_area_finished_goods' AS new_field, 'Excel列名：总投料面积 <成品>' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_成品利用率' AS old_field, 'erp_finished_goods_utilization_rate' AS new_field, 'Excel列名：成品利用率' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_成型方式' AS old_field, 'erp_forming_method' AS new_field, 'Excel列名：成型方式' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_打印标记' AS old_field, 'erp_printing_marking' AS new_field, 'Excel列名：打印标记' AS comment, 'change' AS migration_kind
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
SELECT 'qms_work_order' AS table_name, 'erp_损耗‰' AS old_field, 'erp_loss_per_mille' AS new_field, 'Excel列名：损耗‰' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_料号2' AS old_field, 'erp_part_no_2' AS new_field, 'Excel列名：料号2' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_旧厂内编号' AS old_field, 'erp_old_internal_product_no' AS new_field, 'Excel列名：旧厂内编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_最后入库日期' AS old_field, 'erp_last_receipt_date' AS new_field, 'Excel列名：最后入库日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_未入库数量' AS old_field, 'erp_not_receipt_quantity' AS new_field, 'Excel列名：未入库数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_本卡PCS数' AS old_field, 'erp_current_card_pcs_count' AS new_field, 'Excel列名：本卡PCS数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_本卡工作板数' AS old_field, 'erp_current_card_panel_count' AS new_field, 'Excel列名：本卡工作板数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_材质' AS old_field, 'erp_material' AS new_field, 'Excel列名：材质' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_板厚' AS old_field, 'erp_board_thickness' AS new_field, 'Excel列名：板厚' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_板材名称' AS old_field, 'erp_board_material_name' AS new_field, 'Excel列名：板材名称' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_板材目前库存' AS old_field, 'erp_board_material_current_inventory' AS new_field, 'Excel列名：板材目前库存' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_板材编号' AS old_field, 'erp_board_material_no' AS new_field, 'Excel列名：板材编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_板材规格' AS old_field, 'erp_board_material_specification' AS new_field, 'Excel列名：板材规格' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_板材面积' AS old_field, 'erp_board_material_area' AS new_field, 'Excel列名：板材面积' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_标准用量' AS old_field, 'erp_standard_consumption' AS new_field, 'Excel列名：标准用量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_特殊工艺' AS old_field, 'erp_special_process_technology' AS new_field, 'Excel列名：特殊工艺' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_生产指令号' AS old_field, 'erp_production_order_no' AS new_field, 'Excel列名：生产指令号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_生产通知单号' AS old_field, 'erp_production_notice_no' AS new_field, 'Excel列名：生产通知单号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_生产通知单数量' AS old_field, 'erp_production_notice_quantity' AS new_field, 'Excel列名：生产通知单数量' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_生产通知单面积<成品>' AS old_field, 'erp_production_notice_area_finished_goods' AS new_field, 'Excel列名：生产通知单面积 <成品>' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_管制卡号' AS old_field, 'erp_control_card_no' AS new_field, 'Excel列名：管制卡号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_累计不良' AS old_field, 'erp_cumulative_defect' AS new_field, 'Excel列名：累计不良' AS comment, 'change' AS migration_kind
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
SELECT 'qms_work_order' AS table_name, 'erp_订单数量<生产通知单>' AS old_field, 'erp_order_quantity_production_notice' AS new_field, 'Excel列名：订单数量 <生产通知单>' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_订单类型' AS old_field, 'erp_order_type' AS new_field, 'Excel列名：订单类型' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_订单编号' AS old_field, 'erp_order_no' AS new_field, 'Excel列名：订单编号' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_评审交期' AS old_field, 'erp_review_delivery_date' AS new_field, 'Excel列名：评审交期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_输入日期' AS old_field, 'erp_entry_date' AS new_field, 'Excel列名：输入日期' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_输入者' AS old_field, 'erp_entered_by' AS new_field, 'Excel列名：输入者' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_连片数' AS old_field, 'erp_array_count' AS new_field, 'Excel列名：连片数' AS comment, 'change' AS migration_kind
UNION ALL
SELECT 'qms_work_order' AS table_name, 'erp_铜箔' AS old_field, 'erp_copper_foil' AS new_field, 'Excel列名：铜箔' AS comment, 'change' AS migration_kind
) AS m
JOIN information_schema.columns c ON c.TABLE_SCHEMA=DATABASE() AND c.TABLE_NAME=m.table_name AND c.COLUMN_NAME=m.new_field
WHERE LOWER(c.COLUMN_TYPE) <> 'longtext' OR c.IS_NULLABLE <> 'YES' OR c.COLUMN_DEFAULT IS NOT NULL OR c.EXTRA <> '';

-- qms_material_receipt is deliberately excluded because it is absent in this database.
-- Informational per-tenant counts must agree; subsequent issue queries must return zero rows.

SELECT 'qms_material_issue' AS table_name, 'erp_unit_price_replenishment_e186288c45' AS new_field, `tenant_code`, COUNT(`erp_单价`) AS legacy_non_null_count, COUNT(`erp_unit_price_replenishment_e186288c45`) AS new_non_null_count FROM `qms_material_issue` WHERE BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test' GROUP BY `tenant_code`;
SELECT 'split_value_mismatch' AS issue, 'erp_unit_price_replenishment_e186288c45' AS new_field, `tenant_code`, COUNT(*) AS mismatch_count FROM `qms_material_issue` WHERE BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test' AND NOT (BINARY `erp_单价` <=> BINARY `erp_unit_price_replenishment_e186288c45`) GROUP BY `tenant_code`;
SELECT 'split_value_outside_scope' AS issue, 'erp_unit_price_replenishment_e186288c45' AS new_field, `tenant_code`, COUNT(*) AS unexpected_count FROM `qms_material_issue` WHERE NOT COALESCE((BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test'), FALSE) AND `erp_unit_price_replenishment_e186288c45` IS NOT NULL GROUP BY `tenant_code`;

SELECT 'qms_material_issue' AS table_name, 'erp_unit_price_source_c958a27931' AS new_field, `tenant_code`, COUNT(`erp_单价`) AS legacy_non_null_count, COUNT(`erp_unit_price_source_c958a27931`) AS new_non_null_count FROM `qms_material_issue` WHERE BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test' GROUP BY `tenant_code`;
SELECT 'split_value_mismatch' AS issue, 'erp_unit_price_source_c958a27931' AS new_field, `tenant_code`, COUNT(*) AS mismatch_count FROM `qms_material_issue` WHERE BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test' AND NOT (BINARY `erp_单价` <=> BINARY `erp_unit_price_source_c958a27931`) GROUP BY `tenant_code`;
SELECT 'split_value_outside_scope' AS issue, 'erp_unit_price_source_c958a27931' AS new_field, `tenant_code`, COUNT(*) AS unexpected_count FROM `qms_material_issue` WHERE NOT COALESCE((BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test'), FALSE) AND `erp_unit_price_source_c958a27931` IS NOT NULL GROUP BY `tenant_code`;
SELECT 'unassigned_legacy_value' AS issue, 'erp_单价' AS old_field, `tenant_code`, `source_file`, `sheet_name`, COUNT(*) AS unassigned_count FROM `qms_material_issue` WHERE `erp_单价` IS NOT NULL AND NOT COALESCE(((BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test') OR (BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test')), FALSE) GROUP BY `tenant_code`, `source_file`, `sheet_name`;

SELECT 'qms_material_issue' AS table_name, 'erp_unit_replenishment_26e8962890' AS new_field, `tenant_code`, COUNT(`erp_单位`) AS legacy_non_null_count, COUNT(`erp_unit_replenishment_26e8962890`) AS new_non_null_count FROM `qms_material_issue` WHERE BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test' GROUP BY `tenant_code`;
SELECT 'split_value_mismatch' AS issue, 'erp_unit_replenishment_26e8962890' AS new_field, `tenant_code`, COUNT(*) AS mismatch_count FROM `qms_material_issue` WHERE BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test' AND NOT (BINARY `erp_单位` <=> BINARY `erp_unit_replenishment_26e8962890`) GROUP BY `tenant_code`;
SELECT 'split_value_outside_scope' AS issue, 'erp_unit_replenishment_26e8962890' AS new_field, `tenant_code`, COUNT(*) AS unexpected_count FROM `qms_material_issue` WHERE NOT COALESCE((BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test'), FALSE) AND `erp_unit_replenishment_26e8962890` IS NOT NULL GROUP BY `tenant_code`;

SELECT 'qms_material_issue' AS table_name, 'erp_unit_source_9659f2994f' AS new_field, `tenant_code`, COUNT(`erp_单位`) AS legacy_non_null_count, COUNT(`erp_unit_source_9659f2994f`) AS new_non_null_count FROM `qms_material_issue` WHERE BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test' GROUP BY `tenant_code`;
SELECT 'split_value_mismatch' AS issue, 'erp_unit_source_9659f2994f' AS new_field, `tenant_code`, COUNT(*) AS mismatch_count FROM `qms_material_issue` WHERE BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test' AND NOT (BINARY `erp_单位` <=> BINARY `erp_unit_source_9659f2994f`) GROUP BY `tenant_code`;
SELECT 'split_value_outside_scope' AS issue, 'erp_unit_source_9659f2994f' AS new_field, `tenant_code`, COUNT(*) AS unexpected_count FROM `qms_material_issue` WHERE NOT COALESCE((BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test'), FALSE) AND `erp_unit_source_9659f2994f` IS NOT NULL GROUP BY `tenant_code`;
SELECT 'unassigned_legacy_value' AS issue, 'erp_单位' AS old_field, `tenant_code`, `source_file`, `sheet_name`, COUNT(*) AS unassigned_count FROM `qms_material_issue` WHERE `erp_单位` IS NOT NULL AND NOT COALESCE(((BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test') OR (BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test')), FALSE) GROUP BY `tenant_code`, `source_file`, `sheet_name`;

SELECT 'qms_material_issue' AS table_name, 'erp_internal_product_no_replenishment_9cca17fc3d' AS new_field, `tenant_code`, COUNT(`erp_厂内编号`) AS legacy_non_null_count, COUNT(`erp_internal_product_no_replenishment_9cca17fc3d`) AS new_non_null_count FROM `qms_material_issue` WHERE BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test' GROUP BY `tenant_code`;
SELECT 'split_value_mismatch' AS issue, 'erp_internal_product_no_replenishment_9cca17fc3d' AS new_field, `tenant_code`, COUNT(*) AS mismatch_count FROM `qms_material_issue` WHERE BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test' AND NOT (BINARY `erp_厂内编号` <=> BINARY `erp_internal_product_no_replenishment_9cca17fc3d`) GROUP BY `tenant_code`;
SELECT 'split_value_outside_scope' AS issue, 'erp_internal_product_no_replenishment_9cca17fc3d' AS new_field, `tenant_code`, COUNT(*) AS unexpected_count FROM `qms_material_issue` WHERE NOT COALESCE((BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test'), FALSE) AND `erp_internal_product_no_replenishment_9cca17fc3d` IS NOT NULL GROUP BY `tenant_code`;

SELECT 'qms_material_issue' AS table_name, 'erp_internal_product_no_source_18dfd8dc68' AS new_field, `tenant_code`, COUNT(`erp_厂内编号`) AS legacy_non_null_count, COUNT(`erp_internal_product_no_source_18dfd8dc68`) AS new_non_null_count FROM `qms_material_issue` WHERE BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test' GROUP BY `tenant_code`;
SELECT 'split_value_mismatch' AS issue, 'erp_internal_product_no_source_18dfd8dc68' AS new_field, `tenant_code`, COUNT(*) AS mismatch_count FROM `qms_material_issue` WHERE BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test' AND NOT (BINARY `erp_厂内编号` <=> BINARY `erp_internal_product_no_source_18dfd8dc68`) GROUP BY `tenant_code`;
SELECT 'split_value_outside_scope' AS issue, 'erp_internal_product_no_source_18dfd8dc68' AS new_field, `tenant_code`, COUNT(*) AS unexpected_count FROM `qms_material_issue` WHERE NOT COALESCE((BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test'), FALSE) AND `erp_internal_product_no_source_18dfd8dc68` IS NOT NULL GROUP BY `tenant_code`;
SELECT 'unassigned_legacy_value' AS issue, 'erp_厂内编号' AS old_field, `tenant_code`, `source_file`, `sheet_name`, COUNT(*) AS unassigned_count FROM `qms_material_issue` WHERE `erp_厂内编号` IS NOT NULL AND NOT COALESCE(((BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test') OR (BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test')), FALSE) GROUP BY `tenant_code`, `source_file`, `sheet_name`;

SELECT 'qms_material_issue' AS table_name, 'erp_customer_part_no_replenishment_18b2446684' AS new_field, `tenant_code`, COUNT(`erp_客户料号`) AS legacy_non_null_count, COUNT(`erp_customer_part_no_replenishment_18b2446684`) AS new_non_null_count FROM `qms_material_issue` WHERE BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test' GROUP BY `tenant_code`;
SELECT 'split_value_mismatch' AS issue, 'erp_customer_part_no_replenishment_18b2446684' AS new_field, `tenant_code`, COUNT(*) AS mismatch_count FROM `qms_material_issue` WHERE BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test' AND NOT (BINARY `erp_客户料号` <=> BINARY `erp_customer_part_no_replenishment_18b2446684`) GROUP BY `tenant_code`;
SELECT 'split_value_outside_scope' AS issue, 'erp_customer_part_no_replenishment_18b2446684' AS new_field, `tenant_code`, COUNT(*) AS unexpected_count FROM `qms_material_issue` WHERE NOT COALESCE((BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test'), FALSE) AND `erp_customer_part_no_replenishment_18b2446684` IS NOT NULL GROUP BY `tenant_code`;

SELECT 'qms_material_issue' AS table_name, 'erp_customer_part_no_source_00e16c5278' AS new_field, `tenant_code`, COUNT(`erp_客户料号`) AS legacy_non_null_count, COUNT(`erp_customer_part_no_source_00e16c5278`) AS new_non_null_count FROM `qms_material_issue` WHERE BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test' GROUP BY `tenant_code`;
SELECT 'split_value_mismatch' AS issue, 'erp_customer_part_no_source_00e16c5278' AS new_field, `tenant_code`, COUNT(*) AS mismatch_count FROM `qms_material_issue` WHERE BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test' AND NOT (BINARY `erp_客户料号` <=> BINARY `erp_customer_part_no_source_00e16c5278`) GROUP BY `tenant_code`;
SELECT 'split_value_outside_scope' AS issue, 'erp_customer_part_no_source_00e16c5278' AS new_field, `tenant_code`, COUNT(*) AS unexpected_count FROM `qms_material_issue` WHERE NOT COALESCE((BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test'), FALSE) AND `erp_customer_part_no_source_00e16c5278` IS NOT NULL GROUP BY `tenant_code`;
SELECT 'unassigned_legacy_value' AS issue, 'erp_客户料号' AS old_field, `tenant_code`, `source_file`, `sheet_name`, COUNT(*) AS unassigned_count FROM `qms_material_issue` WHERE `erp_客户料号` IS NOT NULL AND NOT COALESCE(((BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test') OR (BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test')), FALSE) GROUP BY `tenant_code`, `source_file`, `sheet_name`;

SELECT 'qms_material_issue' AS table_name, 'erp_customer_code_replenishment_a38c57442a' AS new_field, `tenant_code`, COUNT(`erp_客户编号`) AS legacy_non_null_count, COUNT(`erp_customer_code_replenishment_a38c57442a`) AS new_non_null_count FROM `qms_material_issue` WHERE BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test' GROUP BY `tenant_code`;
SELECT 'split_value_mismatch' AS issue, 'erp_customer_code_replenishment_a38c57442a' AS new_field, `tenant_code`, COUNT(*) AS mismatch_count FROM `qms_material_issue` WHERE BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test' AND NOT (BINARY `erp_客户编号` <=> BINARY `erp_customer_code_replenishment_a38c57442a`) GROUP BY `tenant_code`;
SELECT 'split_value_outside_scope' AS issue, 'erp_customer_code_replenishment_a38c57442a' AS new_field, `tenant_code`, COUNT(*) AS unexpected_count FROM `qms_material_issue` WHERE NOT COALESCE((BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test'), FALSE) AND `erp_customer_code_replenishment_a38c57442a` IS NOT NULL GROUP BY `tenant_code`;

SELECT 'qms_material_issue' AS table_name, 'erp_customer_code_source_3c7ef4232e' AS new_field, `tenant_code`, COUNT(`erp_客户编号`) AS legacy_non_null_count, COUNT(`erp_customer_code_source_3c7ef4232e`) AS new_non_null_count FROM `qms_material_issue` WHERE BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test' GROUP BY `tenant_code`;
SELECT 'split_value_mismatch' AS issue, 'erp_customer_code_source_3c7ef4232e' AS new_field, `tenant_code`, COUNT(*) AS mismatch_count FROM `qms_material_issue` WHERE BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test' AND NOT (BINARY `erp_客户编号` <=> BINARY `erp_customer_code_source_3c7ef4232e`) GROUP BY `tenant_code`;
SELECT 'split_value_outside_scope' AS issue, 'erp_customer_code_source_3c7ef4232e' AS new_field, `tenant_code`, COUNT(*) AS unexpected_count FROM `qms_material_issue` WHERE NOT COALESCE((BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test'), FALSE) AND `erp_customer_code_source_3c7ef4232e` IS NOT NULL GROUP BY `tenant_code`;
SELECT 'unassigned_legacy_value' AS issue, 'erp_客户编号' AS old_field, `tenant_code`, `source_file`, `sheet_name`, COUNT(*) AS unassigned_count FROM `qms_material_issue` WHERE `erp_客户编号` IS NOT NULL AND NOT COALESCE(((BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test') OR (BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test')), FALSE) GROUP BY `tenant_code`, `source_file`, `sheet_name`;

SELECT 'qms_material_issue' AS table_name, 'erp_currency_replenishment_f8282e9cc3' AS new_field, `tenant_code`, COUNT(`erp_币别`) AS legacy_non_null_count, COUNT(`erp_currency_replenishment_f8282e9cc3`) AS new_non_null_count FROM `qms_material_issue` WHERE BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test' GROUP BY `tenant_code`;
SELECT 'split_value_mismatch' AS issue, 'erp_currency_replenishment_f8282e9cc3' AS new_field, `tenant_code`, COUNT(*) AS mismatch_count FROM `qms_material_issue` WHERE BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test' AND NOT (BINARY `erp_币别` <=> BINARY `erp_currency_replenishment_f8282e9cc3`) GROUP BY `tenant_code`;
SELECT 'split_value_outside_scope' AS issue, 'erp_currency_replenishment_f8282e9cc3' AS new_field, `tenant_code`, COUNT(*) AS unexpected_count FROM `qms_material_issue` WHERE NOT COALESCE((BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test'), FALSE) AND `erp_currency_replenishment_f8282e9cc3` IS NOT NULL GROUP BY `tenant_code`;

SELECT 'qms_material_issue' AS table_name, 'erp_currency_source_893eac34de' AS new_field, `tenant_code`, COUNT(`erp_币别`) AS legacy_non_null_count, COUNT(`erp_currency_source_893eac34de`) AS new_non_null_count FROM `qms_material_issue` WHERE BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test' GROUP BY `tenant_code`;
SELECT 'split_value_mismatch' AS issue, 'erp_currency_source_893eac34de' AS new_field, `tenant_code`, COUNT(*) AS mismatch_count FROM `qms_material_issue` WHERE BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test' AND NOT (BINARY `erp_币别` <=> BINARY `erp_currency_source_893eac34de`) GROUP BY `tenant_code`;
SELECT 'split_value_outside_scope' AS issue, 'erp_currency_source_893eac34de' AS new_field, `tenant_code`, COUNT(*) AS unexpected_count FROM `qms_material_issue` WHERE NOT COALESCE((BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test'), FALSE) AND `erp_currency_source_893eac34de` IS NOT NULL GROUP BY `tenant_code`;
SELECT 'unassigned_legacy_value' AS issue, 'erp_币别' AS old_field, `tenant_code`, `source_file`, `sheet_name`, COUNT(*) AS unassigned_count FROM `qms_material_issue` WHERE `erp_币别` IS NOT NULL AND NOT COALESCE(((BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test') OR (BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test')), FALSE) GROUP BY `tenant_code`, `source_file`, `sheet_name`;

SELECT 'qms_material_issue' AS table_name, 'erp_entry_date_replenishment_0b915d259c' AS new_field, `tenant_code`, COUNT(`erp_输入日期`) AS legacy_non_null_count, COUNT(`erp_entry_date_replenishment_0b915d259c`) AS new_non_null_count FROM `qms_material_issue` WHERE BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test' GROUP BY `tenant_code`;
SELECT 'split_value_mismatch' AS issue, 'erp_entry_date_replenishment_0b915d259c' AS new_field, `tenant_code`, COUNT(*) AS mismatch_count FROM `qms_material_issue` WHERE BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test' AND NOT (BINARY `erp_输入日期` <=> BINARY `erp_entry_date_replenishment_0b915d259c`) GROUP BY `tenant_code`;
SELECT 'split_value_outside_scope' AS issue, 'erp_entry_date_replenishment_0b915d259c' AS new_field, `tenant_code`, COUNT(*) AS unexpected_count FROM `qms_material_issue` WHERE NOT COALESCE((BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test'), FALSE) AND `erp_entry_date_replenishment_0b915d259c` IS NOT NULL GROUP BY `tenant_code`;

SELECT 'qms_material_issue' AS table_name, 'erp_entry_date_source_6d3834179d' AS new_field, `tenant_code`, COUNT(`erp_输入日期`) AS legacy_non_null_count, COUNT(`erp_entry_date_source_6d3834179d`) AS new_non_null_count FROM `qms_material_issue` WHERE BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test' GROUP BY `tenant_code`;
SELECT 'split_value_mismatch' AS issue, 'erp_entry_date_source_6d3834179d' AS new_field, `tenant_code`, COUNT(*) AS mismatch_count FROM `qms_material_issue` WHERE BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test' AND NOT (BINARY `erp_输入日期` <=> BINARY `erp_entry_date_source_6d3834179d`) GROUP BY `tenant_code`;
SELECT 'split_value_outside_scope' AS issue, 'erp_entry_date_source_6d3834179d' AS new_field, `tenant_code`, COUNT(*) AS unexpected_count FROM `qms_material_issue` WHERE NOT COALESCE((BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test'), FALSE) AND `erp_entry_date_source_6d3834179d` IS NOT NULL GROUP BY `tenant_code`;
SELECT 'unassigned_legacy_value' AS issue, 'erp_输入日期' AS old_field, `tenant_code`, `source_file`, `sheet_name`, COUNT(*) AS unassigned_count FROM `qms_material_issue` WHERE `erp_输入日期` IS NOT NULL AND NOT COALESCE(((BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test') OR (BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test')), FALSE) GROUP BY `tenant_code`, `source_file`, `sheet_name`;

SELECT 'qms_material_issue' AS table_name, 'erp_entered_by_replenishment_4129200b1d' AS new_field, `tenant_code`, COUNT(`erp_输入者`) AS legacy_non_null_count, COUNT(`erp_entered_by_replenishment_4129200b1d`) AS new_non_null_count FROM `qms_material_issue` WHERE BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test' GROUP BY `tenant_code`;
SELECT 'split_value_mismatch' AS issue, 'erp_entered_by_replenishment_4129200b1d' AS new_field, `tenant_code`, COUNT(*) AS mismatch_count FROM `qms_material_issue` WHERE BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test' AND NOT (BINARY `erp_输入者` <=> BINARY `erp_entered_by_replenishment_4129200b1d`) GROUP BY `tenant_code`;
SELECT 'split_value_outside_scope' AS issue, 'erp_entered_by_replenishment_4129200b1d' AS new_field, `tenant_code`, COUNT(*) AS unexpected_count FROM `qms_material_issue` WHERE NOT COALESCE((BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test'), FALSE) AND `erp_entered_by_replenishment_4129200b1d` IS NOT NULL GROUP BY `tenant_code`;

SELECT 'qms_material_issue' AS table_name, 'erp_entered_by_source_3e8667c782' AS new_field, `tenant_code`, COUNT(`erp_输入者`) AS legacy_non_null_count, COUNT(`erp_entered_by_source_3e8667c782`) AS new_non_null_count FROM `qms_material_issue` WHERE BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test' GROUP BY `tenant_code`;
SELECT 'split_value_mismatch' AS issue, 'erp_entered_by_source_3e8667c782' AS new_field, `tenant_code`, COUNT(*) AS mismatch_count FROM `qms_material_issue` WHERE BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test' AND NOT (BINARY `erp_输入者` <=> BINARY `erp_entered_by_source_3e8667c782`) GROUP BY `tenant_code`;
SELECT 'split_value_outside_scope' AS issue, 'erp_entered_by_source_3e8667c782' AS new_field, `tenant_code`, COUNT(*) AS unexpected_count FROM `qms_material_issue` WHERE NOT COALESCE((BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test'), FALSE) AND `erp_entered_by_source_3e8667c782` IS NOT NULL GROUP BY `tenant_code`;
SELECT 'unassigned_legacy_value' AS issue, 'erp_输入者' AS old_field, `tenant_code`, `source_file`, `sheet_name`, COUNT(*) AS unassigned_count FROM `qms_material_issue` WHERE `erp_输入者` IS NOT NULL AND NOT COALESCE(((BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test') OR (BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test')), FALSE) GROUP BY `tenant_code`, `source_file`, `sheet_name`;

SET SESSION sql_mode = @erp_migration_saved_sql_mode;
