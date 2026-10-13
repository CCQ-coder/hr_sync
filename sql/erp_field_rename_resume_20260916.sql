-- LIVE RESUME 2026-09-16: state verified against 106.227.69.144/qms
-- MySQL 5.7+/8.0. Select the intended database before running this file.
-- Use a UTF-8 client. STOP synchronization and take a verified BACKUP first.
-- DDL auto-commits; this is not a transaction or an idempotent rerun script.
SET @erp_migration_saved_sql_mode = @@SESSION.sql_mode;
SET SESSION sql_mode = CONCAT_WS(',', NULLIF(@@SESSION.sql_mode, ''), 'NO_BACKSLASH_ESCAPES');
SET NAMES utf8mb4;

-- Resumes only pending tables after qms_material_receipt was found absent. Do not use --force.

ALTER TABLE `qms_process_output_summary`
  CHANGE COLUMN `erp_00:00-04:00` `erp_time_00_00_04_00` LONGTEXT NULL COMMENT 'Excel列名：00:00-04:00',
  CHANGE COLUMN `erp_04:00-08:00` `erp_time_04_00_08_00` LONGTEXT NULL COMMENT 'Excel列名：04:00-08:00',
  CHANGE COLUMN `erp_10:00-12:00` `erp_time_10_00_12_00` LONGTEXT NULL COMMENT 'Excel列名：10:00-12:00',
  CHANGE COLUMN `erp_12:00-15:00` `erp_time_12_00_15_00` LONGTEXT NULL COMMENT 'Excel列名：12:00-15:00',
  CHANGE COLUMN `erp_15:00-17:00` `erp_time_15_00_17_00` LONGTEXT NULL COMMENT 'Excel列名：15:00-17:00',
  CHANGE COLUMN `erp_17:00-20:00` `erp_time_17_00_20_00` LONGTEXT NULL COMMENT 'Excel列名：17:00-20:00',
  CHANGE COLUMN `erp_20:00-22:00` `erp_time_20_00_22_00` LONGTEXT NULL COMMENT 'Excel列名：20:00-22:00',
  CHANGE COLUMN `erp_22:00-00:00` `erp_time_22_00_00_00` LONGTEXT NULL COMMENT 'Excel列名：22:00-00:00',
  CHANGE COLUMN `erp_8:00-10:00` `erp_time_8_00_10_00` LONGTEXT NULL COMMENT 'Excel列名：8:00-10:00',
  CHANGE COLUMN `erp_不良率%` `erp_defect_rate_percent` LONGTEXT NULL COMMENT 'Excel列名：不良率%',
  CHANGE COLUMN `erp_不良面积` `erp_defect_area` LONGTEXT NULL COMMENT 'Excel列名：不良面积',
  CHANGE COLUMN `erp_产值目标<平方/日>` `erp_output_value_target_square_meters_day` LONGTEXT NULL COMMENT 'Excel列名：产值目标 <平方/日>',
  CHANGE COLUMN `erp_全天累计` `erp_full_day_cumulative` LONGTEXT NULL COMMENT 'Excel列名：全天累计',
  CHANGE COLUMN `erp_出勤人数` `erp_attendance_headcount` LONGTEXT NULL COMMENT 'Excel列名：出勤人数',
  CHANGE COLUMN `erp_出勤总工时` `erp_attendance_total_labor_hours` LONGTEXT NULL COMMENT 'Excel列名：出勤总工时',
  CHANGE COLUMN `erp_单双面` `erp_single_double_sided` LONGTEXT NULL COMMENT 'Excel列名：单双面',
  CHANGE COLUMN `erp_在线存板平米` `erp_in_process_board_inventory_square_meters` LONGTEXT NULL COMMENT 'Excel列名：在线存板平米',
  CHANGE COLUMN `erp_工时效率平米/人/时` `erp_labor_hours_efficiency_square_meters_person_hour` LONGTEXT NULL COMMENT 'Excel列名：工时效率 平米/人/时',
  CHANGE COLUMN `erp_工段` `erp_process_section` LONGTEXT NULL COMMENT 'Excel列名：工段',
  CHANGE COLUMN `erp_平均耗时` `erp_average_elapsed_time` LONGTEXT NULL COMMENT 'Excel列名：平均耗时',
  CHANGE COLUMN `erp_报废率%` `erp_scrap_rate_percent` LONGTEXT NULL COMMENT 'Excel列名：报废率%',
  CHANGE COLUMN `erp_报废面积` `erp_scrap_area` LONGTEXT NULL COMMENT 'Excel列名：报废面积',
  CHANGE COLUMN `erp_晚班累计` `erp_night_shift_cumulative` LONGTEXT NULL COMMENT 'Excel列名：晚班累计',
  CHANGE COLUMN `erp_款数` `erp_model_count` LONGTEXT NULL COMMENT 'Excel列名：款数',
  CHANGE COLUMN `erp_款数_全天` `erp_model_count_full_day` LONGTEXT NULL COMMENT 'Excel列名：款数_全天',
  CHANGE COLUMN `erp_款数_晚班` `erp_model_count_night_shift` LONGTEXT NULL COMMENT 'Excel列名：款数_晚班',
  CHANGE COLUMN `erp_款数_白班` `erp_model_count_day_shift` LONGTEXT NULL COMMENT 'Excel列名：款数_白班',
  CHANGE COLUMN `erp_生产面积` `erp_production_area` LONGTEXT NULL COMMENT 'Excel列名：生产面积',
  CHANGE COLUMN `erp_白班累计` `erp_day_shift_cumulative` LONGTEXT NULL COMMENT 'Excel列名：白班累计',
  CHANGE COLUMN `erp_线别` `erp_line` LONGTEXT NULL COMMENT 'Excel列名：线别',
  CHANGE COLUMN `erp_计件单价<每平方>` `erp_piecework_unit_price_per_square_meters` LONGTEXT NULL COMMENT 'Excel列名：计件单价 <每平方>',
  CHANGE COLUMN `erp_计件总额` `erp_piecework_total_amount` LONGTEXT NULL COMMENT 'Excel列名：计件总额',
  CHANGE COLUMN `erp_达成率%` `erp_achievement_rate_percent` LONGTEXT NULL COMMENT 'Excel列名：达成率%';

ALTER TABLE `qms_purchase_order`
  CHANGE COLUMN `erp_HUB仓` `erp_hub_warehouse` LONGTEXT NULL COMMENT 'Excel列名：HUB仓',
  CHANGE COLUMN `erp_一仓库存` `erp_warehouse_1_inventory` LONGTEXT NULL COMMENT 'Excel列名：一仓库存',
  CHANGE COLUMN `erp_三仓库存` `erp_warehouse_3_inventory` LONGTEXT NULL COMMENT 'Excel列名：三仓库存',
  CHANGE COLUMN `erp_上次报价单价` `erp_previous_quotation_unit_price` LONGTEXT NULL COMMENT 'Excel列名：上次报价单价',
  CHANGE COLUMN `erp_上次报价币别` `erp_previous_quotation_currency` LONGTEXT NULL COMMENT 'Excel列名：上次报价币别',
  CHANGE COLUMN `erp_上次报价税率` `erp_previous_quotation_tax_rate` LONGTEXT NULL COMMENT 'Excel列名：上次报价税率',
  CHANGE COLUMN `erp_不含税金额` `erp_tax_exclusive_amount` LONGTEXT NULL COMMENT 'Excel列名：不含税金额',
  CHANGE COLUMN `erp_不含税金额(本币)` `erp_tax_exclusive_amount_local_currency` LONGTEXT NULL COMMENT 'Excel列名：不含税金额(本币)',
  CHANGE COLUMN `erp_主管签名` `erp_supervisor_signature` LONGTEXT NULL COMMENT 'Excel列名：主管签名',
  CHANGE COLUMN `erp_主管签名人` `erp_supervisor_signature_person` LONGTEXT NULL COMMENT 'Excel列名：主管签名人',
  CHANGE COLUMN `erp_主管签名日期` `erp_supervisor_signature_date` LONGTEXT NULL COMMENT 'Excel列名：主管签名日期',
  CHANGE COLUMN `erp_二仓库存` `erp_warehouse_2_inventory` LONGTEXT NULL COMMENT 'Excel列名：二仓库存',
  CHANGE COLUMN `erp_交货ok` `erp_delivery_ok` LONGTEXT NULL COMMENT 'Excel列名：交货ok',
  CHANGE COLUMN `erp_交货地址` `erp_delivery_address` LONGTEXT NULL COMMENT 'Excel列名：交货地址',
  CHANGE COLUMN `erp_交货日期` `erp_delivery_date` LONGTEXT NULL COMMENT 'Excel列名：交货日期',
  CHANGE COLUMN `erp_付款方式` `erp_payment_method` LONGTEXT NULL COMMENT 'Excel列名：付款方式',
  CHANGE COLUMN `erp_停止交货` `erp_stop_delivery` LONGTEXT NULL COMMENT 'Excel列名：停止交货',
  CHANGE COLUMN `erp_其他17` `erp_other_17` LONGTEXT NULL COMMENT 'Excel列名：其他17',
  CHANGE COLUMN `erp_其他18` `erp_other_18` LONGTEXT NULL COMMENT 'Excel列名：其他18',
  CHANGE COLUMN `erp_其他19` `erp_other_19` LONGTEXT NULL COMMENT 'Excel列名：其他19',
  CHANGE COLUMN `erp_其他20` `erp_other_20` LONGTEXT NULL COMMENT 'Excel列名：其他20',
  CHANGE COLUMN `erp_其他bi1` `erp_bi_1` LONGTEXT NULL COMMENT 'Excel列名：其他bi1',
  CHANGE COLUMN `erp_其他mc3` `erp_mc_3` LONGTEXT NULL COMMENT 'Excel列名：其他mc3',
  CHANGE COLUMN `erp_其他mc4` `erp_mc_4` LONGTEXT NULL COMMENT 'Excel列名：其他mc4',
  CHANGE COLUMN `erp_单价` `erp_unit_price` LONGTEXT NULL COMMENT 'Excel列名：单价',
  CHANGE COLUMN `erp_单位` `erp_unit` LONGTEXT NULL COMMENT 'Excel列名：单位',
  CHANGE COLUMN `erp_厂商` `erp_supplier` LONGTEXT NULL COMMENT 'Excel列名：厂商',
  CHANGE COLUMN `erp_厂商全称` `erp_supplier_full_name` LONGTEXT NULL COMMENT 'Excel列名：厂商全称',
  CHANGE COLUMN `erp_厂商手机` `erp_supplier_mobile_phone` LONGTEXT NULL COMMENT 'Excel列名：厂商手机',
  CHANGE COLUMN `erp_厂商电话` `erp_supplier_phone` LONGTEXT NULL COMMENT 'Excel列名：厂商电话',
  CHANGE COLUMN `erp_厂商编号` `erp_supplier_no` LONGTEXT NULL COMMENT 'Excel列名：厂商编号',
  CHANGE COLUMN `erp_厂商联系人` `erp_supplier_contact_person` LONGTEXT NULL COMMENT 'Excel列名：厂商联系人',
  CHANGE COLUMN `erp_厂商负责人` `erp_supplier_responsible_person` LONGTEXT NULL COMMENT 'Excel列名：厂商负责人',
  CHANGE COLUMN `erp_原料名称` `erp_material_name` LONGTEXT NULL COMMENT 'Excel列名：原料名称',
  CHANGE COLUMN `erp_原料大类` `erp_raw_material_major_category` LONGTEXT NULL COMMENT 'Excel列名：原料大类',
  CHANGE COLUMN `erp_原料小类` `erp_raw_material_minor_category` LONGTEXT NULL COMMENT 'Excel列名：原料小类',
  CHANGE COLUMN `erp_原料编号` `erp_material_no` LONGTEXT NULL COMMENT 'Excel列名：原料编号',
  CHANGE COLUMN `erp_含税类别` `erp_tax_inclusive_category` LONGTEXT NULL COMMENT 'Excel列名：含税类别',
  CHANGE COLUMN `erp_四仓库存` `erp_warehouse_4_inventory` LONGTEXT NULL COMMENT 'Excel列名：四仓库存',
  CHANGE COLUMN `erp_备注` `erp_remarks` LONGTEXT NULL COMMENT 'Excel列名：备注',
  CHANGE COLUMN `erp_备货数量` `erp_stock_preparation_quantity` LONGTEXT NULL COMMENT 'Excel列名：备货数量',
  CHANGE COLUMN `erp_审核人` `erp_review_person` LONGTEXT NULL COMMENT 'Excel列名：审核人',
  CHANGE COLUMN `erp_审核日期` `erp_review_date` LONGTEXT NULL COMMENT 'Excel列名：审核日期',
  CHANGE COLUMN `erp_工厂` `erp_factory` LONGTEXT NULL COMMENT 'Excel列名：工厂',
  CHANGE COLUMN `erp_币别` `erp_currency` LONGTEXT NULL COMMENT 'Excel列名：币别',
  CHANGE COLUMN `erp_成本单价` `erp_cost_unit_price` LONGTEXT NULL COMMENT 'Excel列名：成本单价',
  CHANGE COLUMN `erp_换算标准` `erp_conversion_standard` LONGTEXT NULL COMMENT 'Excel列名：换算标准',
  CHANGE COLUMN `erp_数量` `erp_quantity` LONGTEXT NULL COMMENT 'Excel列名：数量',
  CHANGE COLUMN `erp_最后一次入库日期` `erp_last_receipt_date` LONGTEXT NULL COMMENT 'Excel列名：最后一次入库日期',
  CHANGE COLUMN `erp_最小包装数` `erp_minimum_packaging_count` LONGTEXT NULL COMMENT 'Excel列名：最小包装数',
  CHANGE COLUMN `erp_最小采购数` `erp_minimum_purchase_count` LONGTEXT NULL COMMENT 'Excel列名：最小采购数',
  CHANGE COLUMN `erp_月结天数` `erp_monthly_settlement_days` LONGTEXT NULL COMMENT 'Excel列名：月结天数',
  CHANGE COLUMN `erp_标准单位` `erp_standard_unit` LONGTEXT NULL COMMENT 'Excel列名：标准单位',
  CHANGE COLUMN `erp_标准单位数量` `erp_standard_unit_quantity` LONGTEXT NULL COMMENT 'Excel列名：标准单位数量',
  CHANGE COLUMN `erp_欠交货量` `erp_outstanding_delivery_quantity` LONGTEXT NULL COMMENT 'Excel列名：欠交货量',
  CHANGE COLUMN `erp_欠交金额` `erp_outstanding_delivery_amount` LONGTEXT NULL COMMENT 'Excel列名：欠交金额',
  CHANGE COLUMN `erp_目前库存` `erp_current_inventory` LONGTEXT NULL COMMENT 'Excel列名：目前库存',
  CHANGE COLUMN `erp_确认交期` `erp_confirmation_delivery_date` LONGTEXT NULL COMMENT 'Excel列名：确认交期',
  CHANGE COLUMN `erp_确认交期人` `erp_confirmation_delivery_date_person` LONGTEXT NULL COMMENT 'Excel列名：确认交期人',
  CHANGE COLUMN `erp_确认交期修改次数` `erp_confirmation_delivery_date_revision_count` LONGTEXT NULL COMMENT 'Excel列名：确认交期修改次数',
  CHANGE COLUMN `erp_确认交期备注` `erp_confirmation_delivery_date_remarks` LONGTEXT NULL COMMENT 'Excel列名：确认交期备注',
  CHANGE COLUMN `erp_确认交期时间` `erp_confirmation_delivery_date_time` LONGTEXT NULL COMMENT 'Excel列名：确认交期时间',
  CHANGE COLUMN `erp_税率%` `erp_tax_rate_percent` LONGTEXT NULL COMMENT 'Excel列名：税率%',
  CHANGE COLUMN `erp_第一次入库日期` `erp_first_receipt_date` LONGTEXT NULL COMMENT 'Excel列名：第一次入库日期',
  CHANGE COLUMN `erp_签名` `erp_signature` LONGTEXT NULL COMMENT 'Excel列名：签名',
  CHANGE COLUMN `erp_签收OK/退单` `erp_acknowledgement_ok_rejected_order` LONGTEXT NULL COMMENT 'Excel列名：签收OK/退单',
  CHANGE COLUMN `erp_签收人` `erp_acknowledgement_person` LONGTEXT NULL COMMENT 'Excel列名：签收人',
  CHANGE COLUMN `erp_累计交货` `erp_cumulative_delivery` LONGTEXT NULL COMMENT 'Excel列名：累计交货',
  CHANGE COLUMN `erp_累计预交货数量` `erp_cumulative_scheduled_delivery_quantity` LONGTEXT NULL COMMENT 'Excel列名：累计预交货数量',
  CHANGE COLUMN `erp_英文名称` `erp_english_name` LONGTEXT NULL COMMENT 'Excel列名：英文名称',
  CHANGE COLUMN `erp_英文规格` `erp_english_specification` LONGTEXT NULL COMMENT 'Excel列名：英文规格',
  CHANGE COLUMN `erp_营销模式` `erp_business_model` LONGTEXT NULL COMMENT 'Excel列名：营销模式',
  CHANGE COLUMN `erp_规格` `erp_specification` LONGTEXT NULL COMMENT 'Excel列名：规格',
  CHANGE COLUMN `erp_请购单号` `erp_purchase_requisition_no` LONGTEXT NULL COMMENT 'Excel列名：请购单号',
  CHANGE COLUMN `erp_调价类别` `erp_price_adjustment_category` LONGTEXT NULL COMMENT 'Excel列名：调价类别',
  CHANGE COLUMN `erp_输入日期` `erp_entry_date` LONGTEXT NULL COMMENT 'Excel列名：输入日期',
  CHANGE COLUMN `erp_输入者` `erp_entered_by` LONGTEXT NULL COMMENT 'Excel列名：输入者',
  CHANGE COLUMN `erp_部门签名` `erp_department_signature` LONGTEXT NULL COMMENT 'Excel列名：部门签名',
  CHANGE COLUMN `erp_部门签名人` `erp_department_signature_person` LONGTEXT NULL COMMENT 'Excel列名：部门签名人',
  CHANGE COLUMN `erp_部门签名日期` `erp_department_signature_date` LONGTEXT NULL COMMENT 'Excel列名：部门签名日期',
  CHANGE COLUMN `erp_部门请购数量` `erp_department_purchase_requisition_quantity` LONGTEXT NULL COMMENT 'Excel列名：部门请购数量',
  CHANGE COLUMN `erp_采购单号` `erp_purchase_order_no` LONGTEXT NULL COMMENT 'Excel列名：采购单号',
  CHANGE COLUMN `erp_采购周期` `erp_purchase_cycle` LONGTEXT NULL COMMENT 'Excel列名：采购周期',
  CHANGE COLUMN `erp_采购日期` `erp_purchase_date` LONGTEXT NULL COMMENT 'Excel列名：采购日期',
  CHANGE COLUMN `erp_采购明细类别` `erp_purchase_detail_category` LONGTEXT NULL COMMENT 'Excel列名：采购明细类别',
  CHANGE COLUMN `erp_采购类别` `erp_purchase_category` LONGTEXT NULL COMMENT 'Excel列名：采购类别',
  CHANGE COLUMN `erp_采购类别（重复列2）` `erp_purchase_category_duplicate_2` LONGTEXT NULL COMMENT 'Excel列名：采购类别',
  CHANGE COLUMN `erp_采购类别（重复列3）` `erp_purchase_category_duplicate_3` LONGTEXT NULL COMMENT 'Excel列名：采购类别',
  CHANGE COLUMN `erp_金额` `erp_amount` LONGTEXT NULL COMMENT 'Excel列名：金额',
  CHANGE COLUMN `erp_需求日期` `erp_required_date` LONGTEXT NULL COMMENT 'Excel列名：需求日期',
  CHANGE COLUMN `erp_需采购数量` `erp_required_purchase_quantity` LONGTEXT NULL COMMENT 'Excel列名：需采购数量';

ALTER TABLE `qms_work_order`
  CHANGE COLUMN `erp_A板宽` `erp_a_board_width` LONGTEXT NULL COMMENT 'Excel列名：A板宽',
  CHANGE COLUMN `erp_A板总PNL` `erp_a_board_total_pnl` LONGTEXT NULL COMMENT 'Excel列名：A板总PNL',
  CHANGE COLUMN `erp_A板长` `erp_a_board_length` LONGTEXT NULL COMMENT 'Excel列名：A板长',
  CHANGE COLUMN `erp_A板面积` `erp_a_board_area` LONGTEXT NULL COMMENT 'Excel列名：A板面积',
  CHANGE COLUMN `erp_B板宽` `erp_b_board_width` LONGTEXT NULL COMMENT 'Excel列名：B板宽',
  CHANGE COLUMN `erp_B板总PNL` `erp_b_board_total_pnl` LONGTEXT NULL COMMENT 'Excel列名：B板总PNL',
  CHANGE COLUMN `erp_B板长` `erp_b_board_length` LONGTEXT NULL COMMENT 'Excel列名：B板长',
  CHANGE COLUMN `erp_B板面积` `erp_b_board_area` LONGTEXT NULL COMMENT 'Excel列名：B板面积',
  CHANGE COLUMN `erp_C板宽` `erp_c_board_width` LONGTEXT NULL COMMENT 'Excel列名：C板宽',
  CHANGE COLUMN `erp_C板总PNL` `erp_c_board_total_pnl` LONGTEXT NULL COMMENT 'Excel列名：C板总PNL',
  CHANGE COLUMN `erp_C板长` `erp_c_board_length` LONGTEXT NULL COMMENT 'Excel列名：C板长',
  CHANGE COLUMN `erp_C板面积` `erp_c_board_area` LONGTEXT NULL COMMENT 'Excel列名：C板面积',
  CHANGE COLUMN `erp_D板宽` `erp_d_board_width` LONGTEXT NULL COMMENT 'Excel列名：D板宽',
  CHANGE COLUMN `erp_D板长` `erp_d_board_length` LONGTEXT NULL COMMENT 'Excel列名：D板长',
  CHANGE COLUMN `erp_D板面积` `erp_d_board_area` LONGTEXT NULL COMMENT 'Excel列名：D板面积',
  CHANGE COLUMN `erp_MI制作要求1` `erp_mi_manufacturing_required_1` LONGTEXT NULL COMMENT 'Excel列名：MI制作要求1',
  CHANGE COLUMN `erp_MI制作要求2` `erp_mi_manufacturing_required_2` LONGTEXT NULL COMMENT 'Excel列名：MI制作要求2',
  CHANGE COLUMN `erp_MI制作要求3` `erp_mi_manufacturing_required_3` LONGTEXT NULL COMMENT 'Excel列名：MI制作要求3',
  CHANGE COLUMN `erp_PCS宽` `erp_pcs_width` LONGTEXT NULL COMMENT 'Excel列名：PCS宽',
  CHANGE COLUMN `erp_PCS长` `erp_pcs_length` LONGTEXT NULL COMMENT 'Excel列名：PCS长',
  CHANGE COLUMN `erp_PNL宽` `erp_pnl_width` LONGTEXT NULL COMMENT 'Excel列名：PNL宽',
  CHANGE COLUMN `erp_PNL长` `erp_pnl_length` LONGTEXT NULL COMMENT 'Excel列名：PNL长',
  CHANGE COLUMN `erp_SET利用率` `erp_set_utilization_rate` LONGTEXT NULL COMMENT 'Excel列名：SET利用率',
  CHANGE COLUMN `erp_停止领料` `erp_stop_material_issue` LONGTEXT NULL COMMENT 'Excel列名：停止领料',
  CHANGE COLUMN `erp_入库/已结批` `erp_receipt_already_batch_closed` LONGTEXT NULL COMMENT 'Excel列名：入库/已结批',
  CHANGE COLUMN `erp_加急订单` `erp_urgent_order` LONGTEXT NULL COMMENT 'Excel列名：加急订单',
  CHANGE COLUMN `erp_单PCS面积` `erp_single_pcs_area` LONGTEXT NULL COMMENT 'Excel列名：单PCS面积',
  CHANGE COLUMN `erp_厂内编号` `erp_internal_product_no` LONGTEXT NULL COMMENT 'Excel列名：厂内编号',
  CHANGE COLUMN `erp_合拼厂内编号` `erp_combined_panel_internal_product_no` LONGTEXT NULL COMMENT 'Excel列名：合拼厂内编号',
  CHANGE COLUMN `erp_审核人` `erp_review_person` LONGTEXT NULL COMMENT 'Excel列名：审核人',
  CHANGE COLUMN `erp_审核日期` `erp_review_date` LONGTEXT NULL COMMENT 'Excel列名：审核日期',
  CHANGE COLUMN `erp_客户料号` `erp_customer_part_no` LONGTEXT NULL COMMENT 'Excel列名：客户料号',
  CHANGE COLUMN `erp_客户级别` `erp_customer_grade` LONGTEXT NULL COMMENT 'Excel列名：客户级别',
  CHANGE COLUMN `erp_客户编号` `erp_customer_code` LONGTEXT NULL COMMENT 'Excel列名：客户编号',
  CHANGE COLUMN `erp_客户订单` `erp_customer_order` LONGTEXT NULL COMMENT 'Excel列名：客户订单',
  CHANGE COLUMN `erp_客户订单面积<成品>` `erp_customer_order_area_finished_goods` LONGTEXT NULL COMMENT 'Excel列名：客户订单面积 <成品>',
  CHANGE COLUMN `erp_层数` `erp_layer_count` LONGTEXT NULL COMMENT 'Excel列名：层数',
  CHANGE COLUMN `erp_工作板利用率` `erp_panel_utilization_rate` LONGTEXT NULL COMMENT 'Excel列名：工作板利用率',
  CHANGE COLUMN `erp_工艺` `erp_process_technology` LONGTEXT NULL COMMENT 'Excel列名：工艺',
  CHANGE COLUMN `erp_总冲次` `erp_total_punch_cycles` LONGTEXT NULL COMMENT 'Excel列名：总冲次',
  CHANGE COLUMN `erp_总印次` `erp_total_print_cycles` LONGTEXT NULL COMMENT 'Excel列名：总印次',
  CHANGE COLUMN `erp_总投料面积<成品>` `erp_total_material_input_area_finished_goods` LONGTEXT NULL COMMENT 'Excel列名：总投料面积 <成品>',
  CHANGE COLUMN `erp_成品利用率` `erp_finished_goods_utilization_rate` LONGTEXT NULL COMMENT 'Excel列名：成品利用率',
  CHANGE COLUMN `erp_成型方式` `erp_forming_method` LONGTEXT NULL COMMENT 'Excel列名：成型方式',
  CHANGE COLUMN `erp_打印标记` `erp_printing_marking` LONGTEXT NULL COMMENT 'Excel列名：打印标记',
  CHANGE COLUMN `erp_投单面积<板材>` `erp_order_input_area_board_material` LONGTEXT NULL COMMENT 'Excel列名：投单面积 <板材>',
  CHANGE COLUMN `erp_投料数量` `erp_material_input_quantity` LONGTEXT NULL COMMENT 'Excel列名：投料数量',
  CHANGE COLUMN `erp_投料日期` `erp_material_input_date` LONGTEXT NULL COMMENT 'Excel列名：投料日期',
  CHANGE COLUMN `erp_投料正常/异常` `erp_material_input_normal_abnormal` LONGTEXT NULL COMMENT 'Excel列名：投料正常/异常',
  CHANGE COLUMN `erp_投料类型` `erp_material_input_type` LONGTEXT NULL COMMENT 'Excel列名：投料类型',
  CHANGE COLUMN `erp_报废率%` `erp_scrap_rate_percent` LONGTEXT NULL COMMENT 'Excel列名：报废率%',
  CHANGE COLUMN `erp_损耗‰` `erp_loss_per_mille` LONGTEXT NULL COMMENT 'Excel列名：损耗‰',
  CHANGE COLUMN `erp_料号2` `erp_part_no_2` LONGTEXT NULL COMMENT 'Excel列名：料号2',
  CHANGE COLUMN `erp_旧厂内编号` `erp_old_internal_product_no` LONGTEXT NULL COMMENT 'Excel列名：旧厂内编号',
  CHANGE COLUMN `erp_最后入库日期` `erp_last_receipt_date` LONGTEXT NULL COMMENT 'Excel列名：最后入库日期',
  CHANGE COLUMN `erp_未入库数量` `erp_not_receipt_quantity` LONGTEXT NULL COMMENT 'Excel列名：未入库数量',
  CHANGE COLUMN `erp_本卡PCS数` `erp_current_card_pcs_count` LONGTEXT NULL COMMENT 'Excel列名：本卡PCS数',
  CHANGE COLUMN `erp_本卡工作板数` `erp_current_card_panel_count` LONGTEXT NULL COMMENT 'Excel列名：本卡工作板数',
  CHANGE COLUMN `erp_材质` `erp_material` LONGTEXT NULL COMMENT 'Excel列名：材质',
  CHANGE COLUMN `erp_板厚` `erp_board_thickness` LONGTEXT NULL COMMENT 'Excel列名：板厚',
  CHANGE COLUMN `erp_板材名称` `erp_board_material_name` LONGTEXT NULL COMMENT 'Excel列名：板材名称',
  CHANGE COLUMN `erp_板材目前库存` `erp_board_material_current_inventory` LONGTEXT NULL COMMENT 'Excel列名：板材目前库存',
  CHANGE COLUMN `erp_板材编号` `erp_board_material_no` LONGTEXT NULL COMMENT 'Excel列名：板材编号',
  CHANGE COLUMN `erp_板材规格` `erp_board_material_specification` LONGTEXT NULL COMMENT 'Excel列名：板材规格',
  CHANGE COLUMN `erp_板材面积` `erp_board_material_area` LONGTEXT NULL COMMENT 'Excel列名：板材面积',
  CHANGE COLUMN `erp_标准用量` `erp_standard_consumption` LONGTEXT NULL COMMENT 'Excel列名：标准用量',
  CHANGE COLUMN `erp_特殊工艺` `erp_special_process_technology` LONGTEXT NULL COMMENT 'Excel列名：特殊工艺',
  CHANGE COLUMN `erp_生产指令号` `erp_production_order_no` LONGTEXT NULL COMMENT 'Excel列名：生产指令号',
  CHANGE COLUMN `erp_生产通知单号` `erp_production_notice_no` LONGTEXT NULL COMMENT 'Excel列名：生产通知单号',
  CHANGE COLUMN `erp_生产通知单数量` `erp_production_notice_quantity` LONGTEXT NULL COMMENT 'Excel列名：生产通知单数量',
  CHANGE COLUMN `erp_生产通知单面积<成品>` `erp_production_notice_area_finished_goods` LONGTEXT NULL COMMENT 'Excel列名：生产通知单面积 <成品>',
  CHANGE COLUMN `erp_管制卡号` `erp_control_card_no` LONGTEXT NULL COMMENT 'Excel列名：管制卡号',
  CHANGE COLUMN `erp_累计不良` `erp_cumulative_defect` LONGTEXT NULL COMMENT 'Excel列名：累计不良',
  CHANGE COLUMN `erp_累计入库` `erp_cumulative_receipt` LONGTEXT NULL COMMENT 'Excel列名：累计入库',
  CHANGE COLUMN `erp_累计报废` `erp_cumulative_scrap` LONGTEXT NULL COMMENT 'Excel列名：累计报废',
  CHANGE COLUMN `erp_累计领料` `erp_cumulative_material_issue` LONGTEXT NULL COMMENT 'Excel列名：累计领料',
  CHANGE COLUMN `erp_要求交期` `erp_required_delivery_date` LONGTEXT NULL COMMENT 'Excel列名：要求交期',
  CHANGE COLUMN `erp_计划领料` `erp_planned_material_issue` LONGTEXT NULL COMMENT 'Excel列名：计划领料',
  CHANGE COLUMN `erp_订单数量` `erp_order_quantity` LONGTEXT NULL COMMENT 'Excel列名：订单数量',
  CHANGE COLUMN `erp_订单数量<生产通知单>` `erp_order_quantity_production_notice` LONGTEXT NULL COMMENT 'Excel列名：订单数量 <生产通知单>',
  CHANGE COLUMN `erp_订单类型` `erp_order_type` LONGTEXT NULL COMMENT 'Excel列名：订单类型',
  CHANGE COLUMN `erp_订单编号` `erp_order_no` LONGTEXT NULL COMMENT 'Excel列名：订单编号',
  CHANGE COLUMN `erp_评审交期` `erp_review_delivery_date` LONGTEXT NULL COMMENT 'Excel列名：评审交期',
  CHANGE COLUMN `erp_输入日期` `erp_entry_date` LONGTEXT NULL COMMENT 'Excel列名：输入日期',
  CHANGE COLUMN `erp_输入者` `erp_entered_by` LONGTEXT NULL COMMENT 'Excel列名：输入者',
  CHANGE COLUMN `erp_连片数` `erp_array_count` LONGTEXT NULL COMMENT 'Excel列名：连片数',
  CHANGE COLUMN `erp_铜箔` `erp_copper_foil` LONGTEXT NULL COMMENT 'Excel列名：铜箔';

-- qms_material_receipt is intentionally excluded: its table is absent in this database.
-- Backfill only currently empty target cells; legacy columns are retained for verification.

UPDATE `qms_material_issue` SET `erp_unit_price_replenishment_e186288c45` = `erp_单价`
WHERE BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test' AND `erp_unit_price_replenishment_e186288c45` IS NULL AND `erp_单价` IS NOT NULL;

UPDATE `qms_material_issue` SET `erp_unit_price_source_c958a27931` = `erp_单价`
WHERE BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test' AND `erp_unit_price_source_c958a27931` IS NULL AND `erp_单价` IS NOT NULL;

UPDATE `qms_material_issue` SET `erp_unit_replenishment_26e8962890` = `erp_单位`
WHERE BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test' AND `erp_unit_replenishment_26e8962890` IS NULL AND `erp_单位` IS NOT NULL;

UPDATE `qms_material_issue` SET `erp_unit_source_9659f2994f` = `erp_单位`
WHERE BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test' AND `erp_unit_source_9659f2994f` IS NULL AND `erp_单位` IS NOT NULL;

UPDATE `qms_material_issue` SET `erp_internal_product_no_replenishment_9cca17fc3d` = `erp_厂内编号`
WHERE BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test' AND `erp_internal_product_no_replenishment_9cca17fc3d` IS NULL AND `erp_厂内编号` IS NOT NULL;

UPDATE `qms_material_issue` SET `erp_internal_product_no_source_18dfd8dc68` = `erp_厂内编号`
WHERE BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test' AND `erp_internal_product_no_source_18dfd8dc68` IS NULL AND `erp_厂内编号` IS NOT NULL;

UPDATE `qms_material_issue` SET `erp_customer_part_no_replenishment_18b2446684` = `erp_客户料号`
WHERE BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test' AND `erp_customer_part_no_replenishment_18b2446684` IS NULL AND `erp_客户料号` IS NOT NULL;

UPDATE `qms_material_issue` SET `erp_customer_part_no_source_00e16c5278` = `erp_客户料号`
WHERE BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test' AND `erp_customer_part_no_source_00e16c5278` IS NULL AND `erp_客户料号` IS NOT NULL;

UPDATE `qms_material_issue` SET `erp_customer_code_replenishment_a38c57442a` = `erp_客户编号`
WHERE BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test' AND `erp_customer_code_replenishment_a38c57442a` IS NULL AND `erp_客户编号` IS NOT NULL;

UPDATE `qms_material_issue` SET `erp_customer_code_source_3c7ef4232e` = `erp_客户编号`
WHERE BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test' AND `erp_customer_code_source_3c7ef4232e` IS NULL AND `erp_客户编号` IS NOT NULL;

UPDATE `qms_material_issue` SET `erp_currency_replenishment_f8282e9cc3` = `erp_币别`
WHERE BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test' AND `erp_currency_replenishment_f8282e9cc3` IS NULL AND `erp_币别` IS NOT NULL;

UPDATE `qms_material_issue` SET `erp_currency_source_893eac34de` = `erp_币别`
WHERE BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test' AND `erp_currency_source_893eac34de` IS NULL AND `erp_币别` IS NOT NULL;

UPDATE `qms_material_issue` SET `erp_entry_date_replenishment_0b915d259c` = `erp_输入日期`
WHERE BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test' AND `erp_entry_date_replenishment_0b915d259c` IS NULL AND `erp_输入日期` IS NOT NULL;

UPDATE `qms_material_issue` SET `erp_entry_date_source_6d3834179d` = `erp_输入日期`
WHERE BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test' AND `erp_entry_date_source_6d3834179d` IS NULL AND `erp_输入日期` IS NOT NULL;

UPDATE `qms_material_issue` SET `erp_entered_by_replenishment_4129200b1d` = `erp_输入者`
WHERE BINARY `source_file` = BINARY '补料资料.xls' AND BINARY `sheet_name` = BINARY 'Test' AND `erp_entered_by_replenishment_4129200b1d` IS NULL AND `erp_输入者` IS NOT NULL;

UPDATE `qms_material_issue` SET `erp_entered_by_source_3e8667c782` = `erp_输入者`
WHERE BINARY `source_file` = BINARY '原料出库单资料.xls.xls' AND BINARY `sheet_name` = BINARY 'Test' AND `erp_entered_by_source_3e8667c782` IS NULL AND `erp_输入者` IS NOT NULL;

-- No DROP COLUMN and no contract step are included in this recovery script.

SET SESSION sql_mode = @erp_migration_saved_sql_mode;
