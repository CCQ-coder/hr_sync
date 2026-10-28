-- QMS / ERP BI 看板查询（MySQL 8.0+）
-- 使用方法：
--   1. 将每条组件 SQL 单独复制到 BI 数据集即可执行；不依赖前置 SET。
--   2. 每个“组件”下面是一条可单独配置到 BI 组件的数据集 SQL。
--   3. ERP 同步表的 erp_* 字段均为 LONGTEXT；每条查询均已处理空值、千分位及日期文本。
-- 口径：
--   销售额以客户订单的“含税金额（本位币）”为准；采购额以采购订单的“金额”为准；金额均转换为万元。
--   所有查询都排除 status <> ACTIVE 的 ERP 同步记录。

-- 每条组件 SQL 都可独立执行：默认租户直接写为 BINARY 'customer-b'，
-- 需要查询其他租户时，请将该字面量替换为对应的租户编码；统计截止日期均直接使用 CURDATE()。

/* ========================================================================== */
/* 销售可视化数据                                                            */
/* ========================================================================== */

-- 组件：本月销售量（万元）
WITH sales_orders AS (
    SELECT
        STR_TO_DATE(REPLACE(LEFT(TRIM(`erp_order_placed_date`), 10), '/', '-'), '%Y-%m-%d') AS biz_date,
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_tax_inclusive_amount_local_currency`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS amount
    FROM qms_customer_order
    WHERE tenant_code = BINARY 'customer-b' AND status = 'ACTIVE'
)
SELECT
    COALESCE(ROUND(SUM(CASE
        WHEN biz_date >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
         AND biz_date <  DATE_ADD(DATE_FORMAT(CURDATE(), '%Y-%m-01'), INTERVAL 1 MONTH)
        THEN amount END) / 10000, 2), 0) AS 本月销售额_万元
FROM sales_orders;

-- 组件：上月销售量（万元）
WITH sales_orders AS (
    SELECT
        STR_TO_DATE(REPLACE(LEFT(TRIM(`erp_order_placed_date`), 10), '/', '-'), '%Y-%m-%d') AS biz_date,
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_tax_inclusive_amount_local_currency`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS amount
    FROM qms_customer_order
    WHERE tenant_code = BINARY 'customer-b' AND status = 'ACTIVE'
)
SELECT
    COALESCE(ROUND(SUM(CASE
        WHEN biz_date >= DATE_SUB(DATE_FORMAT(CURDATE(), '%Y-%m-01'), INTERVAL 1 MONTH)
         AND biz_date <  DATE_FORMAT(CURDATE(), '%Y-%m-01')
        THEN amount END) / 10000, 2), 0) AS 上月销售额_万元
FROM sales_orders;

-- 组件：本年销售量（万元）
WITH sales_orders AS (
    SELECT
        STR_TO_DATE(REPLACE(LEFT(TRIM(`erp_order_placed_date`), 10), '/', '-'), '%Y-%m-%d') AS biz_date,
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_tax_inclusive_amount_local_currency`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS amount
    FROM qms_customer_order
    WHERE tenant_code = BINARY 'customer-b' AND status = 'ACTIVE'
)
SELECT
    COALESCE(ROUND(SUM(CASE WHEN YEAR(biz_date) = YEAR(CURDATE()) THEN amount END) / 10000, 2), 0) AS 本年销售额_万元
FROM sales_orders;

-- 组件：本月客户跟单员接单统计（环形图；value 使用订单数）
WITH orders AS (
    SELECT
        STR_TO_DATE(REPLACE(LEFT(TRIM(`erp_order_placed_date`), 10), '/', '-'), '%Y-%m-%d') AS order_date,
        NULLIF(TRIM(`erp_order_clerk`), '') AS follow_up_staff,
        NULLIF(TRIM(`erp_order_no`), '') AS order_no,
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_tax_inclusive_amount_local_currency`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS amount
    FROM qms_customer_order
    WHERE tenant_code = BINARY 'customer-b' AND status = 'ACTIVE'
)
SELECT
    COALESCE(follow_up_staff, '未分配') AS name,
    COUNT(DISTINCT order_no) AS value,
    ROUND(SUM(amount) / 10000, 2) AS 接单金额_万元
FROM orders
WHERE order_date >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
  AND order_date <  DATE_ADD(DATE_FORMAT(CURDATE(), '%Y-%m-01'), INTERVAL 1 MONTH)
GROUP BY COALESCE(follow_up_staff, '未分配')
ORDER BY value DESC, 接单金额_万元 DESC;

-- 组件：本月各客户接单排名（万元）
WITH orders AS (
    SELECT
        STR_TO_DATE(REPLACE(LEFT(TRIM(`erp_order_placed_date`), 10), '/', '-'), '%Y-%m-%d') AS order_date,
        NULLIF(TRIM(`erp_customer`), '') AS customer_name,
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_tax_inclusive_amount_local_currency`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS amount
    FROM qms_customer_order
    WHERE tenant_code = BINARY 'customer-b' AND status = 'ACTIVE'
)
SELECT
    COALESCE(customer_name, '未维护客户') AS 客户,
    ROUND(SUM(amount) / 10000, 2) AS 接单金额_万元
FROM orders
WHERE order_date >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
  AND order_date <  DATE_ADD(DATE_FORMAT(CURDATE(), '%Y-%m-01'), INTERVAL 1 MONTH)
GROUP BY COALESCE(customer_name, '未维护客户')
ORDER BY 接单金额_万元 DESC
LIMIT 10;

-- 组件：未交货订单明细
WITH open_orders AS (
    SELECT
        NULLIF(TRIM(`erp_customer`), '') AS customer_name,
        NULLIF(TRIM(`erp_order_no`), '') AS order_no,
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_order_placed_quantity`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS order_quantity,
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_outstanding_delivery_quantity`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS open_quantity,
        STR_TO_DATE(REPLACE(LEFT(TRIM(COALESCE(`erp_final_delivery_date`, `erp_delivery_date`)), 10), '/', '-'), '%Y-%m-%d') AS due_date,
        NULLIF(TRIM(`erp_stop_delivery`), '') AS stop_delivery
    FROM qms_customer_order
    WHERE tenant_code = BINARY 'customer-b' AND status = 'ACTIVE'
)
SELECT
    ROW_NUMBER() OVER (ORDER BY due_date IS NULL, due_date, open_quantity DESC) AS 行号,
    customer_name AS 客户,
    order_no AS 订单编号,
    order_quantity AS 数量,
    open_quantity AS 未交货数量,
    due_date AS 交期
FROM open_orders
WHERE open_quantity > 0
  AND COALESCE(stop_delivery, '') NOT IN ('Y', 'y', '是', '1', 'TRUE', 'true')
ORDER BY due_date IS NULL, due_date, open_quantity DESC
LIMIT 50;

-- 组件：近 2 年各月销售额对比（万元）
WITH RECURSIVE calendar AS (
    SELECT DATE_SUB(DATE_FORMAT(CURDATE(), '%Y-01-01'), INTERVAL 1 YEAR) AS month_start
    UNION ALL
    SELECT DATE_ADD(month_start, INTERVAL 1 MONTH)
    FROM calendar
    WHERE month_start < DATE_FORMAT(CURDATE(), '%Y-12-01')
),
sales_orders AS (
    SELECT
        STR_TO_DATE(REPLACE(LEFT(TRIM(`erp_order_placed_date`), 10), '/', '-'), '%Y-%m-%d') AS biz_date,
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_tax_inclusive_amount_local_currency`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS amount
    FROM qms_customer_order
    WHERE tenant_code = BINARY 'customer-b' AND status = 'ACTIVE'
),
monthly_sales AS (
    SELECT DATE_FORMAT(biz_date, '%Y-%m-01') AS month_start, SUM(amount) AS sales_amount
    FROM sales_orders
    WHERE YEAR(biz_date) IN (YEAR(CURDATE()) - 1, YEAR(CURDATE()))
    GROUP BY DATE_FORMAT(biz_date, '%Y-%m-01')
)
SELECT
    CONCAT(MONTH(c.month_start), '月') AS month,
    COALESCE(ROUND(s.sales_amount / 10000, 2), 0) AS sales,
    CONCAT(YEAR(c.month_start), '年') AS `group`
FROM calendar c
LEFT JOIN monthly_sales s
  ON s.month_start = DATE_FORMAT(c.month_start, '%Y-%m-01')
ORDER BY c.month_start;

-- 组件：本年各跟单员接单统计（万元）
WITH orders AS (
    SELECT
        STR_TO_DATE(REPLACE(LEFT(TRIM(`erp_order_placed_date`), 10), '/', '-'), '%Y-%m-%d') AS order_date,
        NULLIF(TRIM(`erp_order_clerk`), '') AS follow_up_staff,
        NULLIF(TRIM(`erp_order_no`), '') AS order_no,
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_tax_inclusive_amount_local_currency`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS amount
    FROM qms_customer_order
    WHERE tenant_code = BINARY 'customer-b' AND status = 'ACTIVE'
)
SELECT
    CONCAT(MONTH(order_date), '月') AS month,
    ROUND(SUM(amount) / 10000, 2) AS sales,
    COALESCE(follow_up_staff, '未分配') AS `group`
FROM orders
WHERE YEAR(order_date) = YEAR(CURDATE())
GROUP BY
    MONTH(order_date),
    CONCAT(MONTH(order_date), '月'),
    COALESCE(follow_up_staff, '未分配')
ORDER BY MONTH(order_date), `group`;

-- 组件：客户订单金额对比排名榜（单位：万元）
WITH orders AS (
    SELECT
        STR_TO_DATE(REPLACE(LEFT(TRIM(`erp_order_placed_date`), 10), '/', '-'), '%Y-%m-%d') AS order_date,
        NULLIF(TRIM(`erp_customer`), '') AS customer_name,
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_tax_inclusive_amount_local_currency`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS amount
    FROM qms_customer_order
    WHERE tenant_code = BINARY 'customer-b' AND status = 'ACTIVE'
),
ranked AS (
    SELECT COALESCE(customer_name, '未维护客户') AS customer_name, SUM(amount) AS amount
    FROM orders
    WHERE YEAR(order_date) = YEAR(CURDATE())
    GROUP BY COALESCE(customer_name, '未维护客户')
)
SELECT
    DENSE_RANK() OVER (ORDER BY amount DESC) AS 排名,
    customer_name AS 客户,
    ROUND(amount / 10000, 2) AS 订单金额_万元,
    ROUND(amount / NULLIF(SUM(amount) OVER (), 0) * 100, 2) AS 占比_百分比
FROM ranked
ORDER BY amount DESC
LIMIT 10;

/* ========================================================================== */
/* 采购可视化数据                                                            */
/* ========================================================================== */

-- 组件：本月采购金额（万元）
WITH po AS (
    SELECT
        STR_TO_DATE(REPLACE(LEFT(TRIM(`erp_purchase_date`), 10), '/', '-'), '%Y-%m-%d') AS purchase_date,
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_amount`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS amount
    FROM qms_purchase_order
    WHERE tenant_code = BINARY 'customer-b' AND status = 'ACTIVE'
)
SELECT
    COALESCE(ROUND(SUM(CASE
        WHEN purchase_date >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
         AND purchase_date <  DATE_ADD(DATE_FORMAT(CURDATE(), '%Y-%m-01'), INTERVAL 1 MONTH)
        THEN amount END) / 10000, 2), 0) AS 本月采购金额_万元
FROM po;

-- 组件：本月采购单数
WITH po AS (
    SELECT
        STR_TO_DATE(REPLACE(LEFT(TRIM(`erp_purchase_date`), 10), '/', '-'), '%Y-%m-%d') AS purchase_date,
        NULLIF(TRIM(`erp_purchase_order_no`), '') AS po_no
    FROM qms_purchase_order
    WHERE tenant_code = BINARY 'customer-b' AND status = 'ACTIVE'
)
SELECT
    COUNT(DISTINCT CASE
        WHEN purchase_date >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
         AND purchase_date <  DATE_ADD(DATE_FORMAT(CURDATE(), '%Y-%m-01'), INTERVAL 1 MONTH)
        THEN po_no END) AS 本月采购单数
FROM po;

-- 组件：供应商准时交付率（本月，百分比）
WITH po AS (
    SELECT
        STR_TO_DATE(REPLACE(LEFT(TRIM(`erp_confirmation_delivery_date`), 10), '/', '-'), '%Y-%m-%d') AS confirmed_due_date,
        STR_TO_DATE(REPLACE(LEFT(TRIM(`erp_delivery_date`), 10), '/', '-'), '%Y-%m-%d') AS delivered_date
    FROM qms_purchase_order
    WHERE tenant_code = BINARY 'customer-b' AND status = 'ACTIVE'
)
SELECT
    ROUND(100 * SUM(CASE
        WHEN delivered_date >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
         AND delivered_date <  DATE_ADD(DATE_FORMAT(CURDATE(), '%Y-%m-01'), INTERVAL 1 MONTH)
         AND confirmed_due_date IS NOT NULL
         AND delivered_date <= confirmed_due_date THEN 1 ELSE 0 END)
      / NULLIF(SUM(CASE
        WHEN delivered_date >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
         AND delivered_date <  DATE_ADD(DATE_FORMAT(CURDATE(), '%Y-%m-01'), INTERVAL 1 MONTH)
         AND confirmed_due_date IS NOT NULL THEN 1 ELSE 0 END), 0), 2) AS 供应商准时交付率_百分比
FROM po;

-- 组件：未交货采购订单
WITH open_po AS (
    SELECT
        NULLIF(TRIM(`erp_purchase_order_no`), '') AS purchase_order_no,
        NULLIF(TRIM(`erp_material_no`), '') AS material_no,
        NULLIF(TRIM(`erp_material_name`), '') AS material_name,
        NULLIF(TRIM(`erp_supplier_full_name`), '') AS supplier_name,
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_quantity`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS purchase_quantity,
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_outstanding_delivery_quantity`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS open_quantity,
        NULLIF(TRIM(`erp_unit`), '') AS unit_name,
        STR_TO_DATE(REPLACE(LEFT(TRIM(`erp_purchase_date`), 10), '/', '-'), '%Y-%m-%d') AS purchase_date,
        NULLIF(TRIM(`erp_stop_delivery`), '') AS stop_delivery
    FROM qms_purchase_order
    WHERE tenant_code = BINARY 'customer-b' AND status = 'ACTIVE'
)
SELECT
    ROW_NUMBER() OVER (ORDER BY purchase_date IS NULL, purchase_date, open_quantity DESC) AS 行号,
    purchase_order_no AS 采购单号,
    material_no AS 原料编号,
    material_name AS 原料名称,
    supplier_name AS 厂商,
    purchase_quantity AS 采购数量,
    open_quantity AS 未交货数量,
    unit_name AS 单位,
    purchase_date AS 下单日期
FROM open_po
WHERE open_quantity > 0
  AND COALESCE(stop_delivery, '') NOT IN ('Y', 'y', '是', '1', 'TRUE', 'true')
ORDER BY purchase_date IS NULL, purchase_date, open_quantity DESC
LIMIT 50;

-- 组件：供应商采购占用（本月，环形图）
WITH po AS (
    SELECT
        STR_TO_DATE(REPLACE(LEFT(TRIM(`erp_purchase_date`), 10), '/', '-'), '%Y-%m-%d') AS purchase_date,
        COALESCE(NULLIF(TRIM(`erp_supplier_full_name`), ''), NULLIF(TRIM(`erp_supplier`), ''), '未维护供应商') AS supplier_name,
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_amount`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS amount
    FROM qms_purchase_order
    WHERE tenant_code = BINARY 'customer-b' AND status = 'ACTIVE'
)
SELECT supplier_name AS name, ROUND(SUM(amount) / 10000, 2) AS value
FROM po
WHERE purchase_date >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
  AND purchase_date <  DATE_ADD(DATE_FORMAT(CURDATE(), '%Y-%m-01'), INTERVAL 1 MONTH)
GROUP BY supplier_name
ORDER BY value DESC
LIMIT 10;

-- 组件：每月板材采购金额与订单量（近 12 个月）
WITH RECURSIVE months AS (
    SELECT DATE_SUB(DATE_FORMAT(CURDATE(), '%Y-%m-01'), INTERVAL 11 MONTH) AS month_start
    UNION ALL
    SELECT DATE_ADD(month_start, INTERVAL 1 MONTH)
    FROM months
    WHERE month_start < DATE_FORMAT(CURDATE(), '%Y-%m-01')
),
po AS (
    SELECT
        STR_TO_DATE(REPLACE(LEFT(TRIM(`erp_purchase_date`), 10), '/', '-'), '%Y-%m-%d') AS purchase_date,
        NULLIF(TRIM(`erp_purchase_order_no`), '') AS po_no,
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_amount`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS amount
    FROM qms_purchase_order
    WHERE tenant_code = BINARY 'customer-b' AND status = 'ACTIVE'
)
SELECT
    DATE_FORMAT(m.month_start, '%Y-%m') AS 月份,
    COALESCE(ROUND(SUM(po.amount) / 10000, 2), 0) AS 采购金额_万元,
    COUNT(DISTINCT po.po_no) AS 采购单数
FROM months m
LEFT JOIN po
    ON po.purchase_date >= m.month_start
   AND po.purchase_date < DATE_ADD(m.month_start, INTERVAL 1 MONTH)
GROUP BY m.month_start
ORDER BY m.month_start;

-- 组件：本年各物料采购数量（万）
WITH po AS (
    SELECT
        STR_TO_DATE(REPLACE(LEFT(TRIM(`erp_purchase_date`), 10), '/', '-'), '%Y-%m-%d') AS purchase_date,
        COALESCE(NULLIF(TRIM(`erp_material_name`), ''), NULLIF(TRIM(`erp_material_no`), ''), '未维护物料') AS material_name,
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_quantity`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS quantity
    FROM qms_purchase_order
    WHERE tenant_code = BINARY 'customer-b' AND status = 'ACTIVE'
)
SELECT material_name AS 物料, ROUND(SUM(quantity) / 10000, 4) AS 采购数量_万
FROM po
WHERE YEAR(purchase_date) = YEAR(CURDATE())
GROUP BY material_name
ORDER BY 采购数量_万 DESC
LIMIT 10;

-- 组件：本年供应商采购额排名
WITH po AS (
    SELECT
        STR_TO_DATE(REPLACE(LEFT(TRIM(`erp_purchase_date`), 10), '/', '-'), '%Y-%m-%d') AS purchase_date,
        COALESCE(NULLIF(TRIM(`erp_supplier_full_name`), ''), NULLIF(TRIM(`erp_supplier`), ''), '未维护供应商') AS supplier_name,
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_amount`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS amount
    FROM qms_purchase_order
    WHERE tenant_code = BINARY 'customer-b' AND status = 'ACTIVE'
)
SELECT
    DENSE_RANK() OVER (ORDER BY SUM(amount) DESC) AS 排名,
    supplier_name AS 供应商,
    ROUND(SUM(amount) / 10000, 2) AS 采购金额_万元
FROM po
WHERE YEAR(purchase_date) = YEAR(CURDATE())
GROUP BY supplier_name
ORDER BY 采购金额_万元 DESC
LIMIT 10;

-- 组件：供应商交付准时率（本年）
WITH delivery AS (
    SELECT
        COALESCE(NULLIF(TRIM(`erp_supplier_full_name`), ''), NULLIF(TRIM(`erp_supplier`), ''), '未维护供应商') AS supplier_name,
        STR_TO_DATE(REPLACE(LEFT(TRIM(`erp_confirmation_delivery_date`), 10), '/', '-'), '%Y-%m-%d') AS due_date,
        STR_TO_DATE(REPLACE(LEFT(TRIM(`erp_delivery_date`), 10), '/', '-'), '%Y-%m-%d') AS delivered_date
    FROM qms_purchase_order
    WHERE tenant_code = BINARY 'customer-b' AND status = 'ACTIVE'
)
SELECT
    supplier_name AS 供应商,
    COUNT(*) AS 已交付明细数,
    SUM(delivered_date <= due_date) AS 准时明细数,
    ROUND(100 * SUM(delivered_date <= due_date) / NULLIF(COUNT(*), 0), 2) AS 准时率_百分比
FROM delivery
WHERE YEAR(delivered_date) = YEAR(CURDATE())
  AND due_date IS NOT NULL
GROUP BY supplier_name
ORDER BY 准时率_百分比 DESC, 已交付明细数 DESC
LIMIT 10;

/* ========================================================================== */
/* 仓库可视化数据                                                            */
/* ========================================================================== */

-- 组件：成品库存（面积）
-- 成品库存面积 = 库存数量 × 单位面积；优先使用本次入库面积/本次入库量，
-- 若该两个 ERP 字段缺失，则回退到关联工单的 single_pcs_area。
WITH finished AS (
    SELECT
        NULLIF(TRIM(`erp_work_order_no`), '') AS work_order_no,
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_finished_goods_inventory`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS stock_quantity,
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_receipt_area_production`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS receipt_area,
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_current_receipt_quantity`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS receipt_quantity
    FROM qms_finished_goods_receipt
    WHERE tenant_code = BINARY 'customer-b' AND status = 'ACTIVE'
)
SELECT
    ROUND(SUM(f.stock_quantity * COALESCE(NULLIF(f.receipt_area / NULLIF(f.receipt_quantity, 0), 0), wo.single_pcs_area, 0)) / 10000, 2) AS 成品库存面积_万平方米
FROM finished f
LEFT JOIN qms_work_order wo
  ON wo.tenant_code = BINARY 'customer-b'
 AND BINARY wo.work_order_no = BINARY f.work_order_no
 AND wo.status = 'ACTIVE';

-- 组件：成品库存（万元）
WITH finished AS (
    SELECT
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_finished_goods_inventory_amount`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS stock_amount
    FROM qms_finished_goods_receipt
    WHERE tenant_code = BINARY 'customer-b' AND status = 'ACTIVE'
)
SELECT
    ROUND(SUM(stock_amount) / 10000, 2) AS 成品库存金额_万元
FROM finished;

-- 组件：板材库存（面积）
WITH raw_material AS (
    SELECT
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_inventory_area`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS stock_area
    FROM qms_material
    WHERE tenant_code = BINARY 'customer-b' AND status = 'ACTIVE'
)
SELECT
    ROUND(SUM(stock_area) / 10000, 2) AS 板材库存面积_万平方米
FROM raw_material;

-- 组件：板材入库排行榜（面积）
WITH material AS (
    SELECT
        COALESCE(NULLIF(TRIM(`erp_material_name`), ''), NULLIF(TRIM(`erp_material_no`), ''), '未维护物料') AS material_name,
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_inventory_area`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS stock_area
    FROM qms_material
    WHERE tenant_code = BINARY 'customer-b' AND status = 'ACTIVE'
)
SELECT material_name AS 板材, ROUND(SUM(stock_area), 2) AS 库存面积
FROM material
GROUP BY material_name
ORDER BY 库存面积 DESC
LIMIT 10;

-- 组件：物料用量占比（本月；环形图）
WITH issue AS (
    SELECT
        STR_TO_DATE(REPLACE(LEFT(TRIM(`erp_material_issue_date`), 10), '/', '-'), '%Y-%m-%d') AS issue_date,
        COALESCE(NULLIF(TRIM(`erp_raw_material_major_category`), ''), NULLIF(TRIM(`erp_original_material_name`), ''), '未维护分类') AS material_category,
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_current_material_issue_quantity`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS issue_quantity
    FROM qms_material_issue
    WHERE tenant_code = BINARY 'customer-b' AND status = 'ACTIVE'
)
SELECT material_category AS name, ROUND(SUM(issue_quantity), 2) AS value
FROM issue
WHERE issue_date >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
  AND issue_date <  DATE_ADD(DATE_FORMAT(CURDATE(), '%Y-%m-01'), INTERVAL 1 MONTH)
GROUP BY material_category
ORDER BY value DESC
LIMIT 10;

-- 组件：物料领用明细
WITH issue AS (
    SELECT
        NULLIF(TRIM(`erp_material_issue_no`), '') AS issue_no,
        COALESCE(NULLIF(TRIM(`erp_original_material_name`), ''), NULLIF(TRIM(`erp_board_material_name`), ''), NULLIF(TRIM(`erp_material_no_source_3b3dc2fa70`), '')) AS material_name,
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_current_material_issue_quantity`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS issue_quantity,
        NULLIF(TRIM(COALESCE(`erp_unit_replenishment_26e8962890`, `erp_unit_source_9659f2994f`)), '') AS unit_name,
        COALESCE(NULLIF(TRIM(`erp_warehouse_name`), ''), NULLIF(TRIM(`erp_bin`), '')) AS warehouse_name,
        STR_TO_DATE(REPLACE(LEFT(TRIM(`erp_material_issue_date`), 10), '/', '-'), '%Y-%m-%d') AS issue_date
    FROM qms_material_issue
    WHERE tenant_code = BINARY 'customer-b' AND status = 'ACTIVE'
)
SELECT
    ROW_NUMBER() OVER (ORDER BY issue_date DESC, issue_no) AS 行号,
    issue_no AS 领料单号,
    material_name AS 物料名称,
    issue_quantity AS 数量,
    unit_name AS 单位,
    warehouse_name AS 仓库,
    issue_date AS 领料日期
FROM issue
ORDER BY issue_date DESC, issue_no
LIMIT 50;

-- 组件：成品库存排行榜（面积）
WITH finished AS (
    SELECT
        NULLIF(TRIM(`erp_work_order_no`), '') AS work_order_no,
        COALESCE(NULLIF(TRIM(`erp_internal_product_no`), ''), NULLIF(TRIM(`erp_customer_part_no`), ''), '未维护产品') AS product_name,
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_finished_goods_inventory`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS stock_quantity,
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_receipt_area_production`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS receipt_area,
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_current_receipt_quantity`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS receipt_quantity
    FROM qms_finished_goods_receipt
    WHERE tenant_code = BINARY 'customer-b' AND status = 'ACTIVE'
)
SELECT
    f.product_name AS 产品,
    ROUND(SUM(f.stock_quantity * COALESCE(NULLIF(f.receipt_area / NULLIF(f.receipt_quantity, 0), 0), wo.single_pcs_area, 0)), 2) AS 库存面积
FROM finished f
LEFT JOIN qms_work_order wo
  ON wo.tenant_code = BINARY 'customer-b'
 AND BINARY wo.work_order_no = BINARY f.work_order_no
 AND wo.status = 'ACTIVE'
GROUP BY f.product_name
ORDER BY 库存面积 DESC
LIMIT 10;

-- 组件：近一年成品出入库对比分析（面积）
WITH RECURSIVE months AS (
    SELECT DATE_SUB(DATE_FORMAT(CURDATE(), '%Y-%m-01'), INTERVAL 11 MONTH) AS month_start
    UNION ALL
    SELECT DATE_ADD(month_start, INTERVAL 1 MONTH) FROM months
    WHERE month_start < DATE_FORMAT(CURDATE(), '%Y-%m-01')
),
inbound AS (
    SELECT
        STR_TO_DATE(REPLACE(LEFT(TRIM(`erp_receipt_date`), 10), '/', '-'), '%Y-%m-%d') AS biz_date,
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_receipt_area_production`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS area
    FROM qms_finished_goods_receipt
    WHERE tenant_code = BINARY 'customer-b' AND status = 'ACTIVE'
),
outbound AS (
    SELECT
        STR_TO_DATE(REPLACE(LEFT(TRIM(`erp_delivery_date`), 10), '/', '-'), '%Y-%m-%d') AS biz_date,
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_issue_area_square_meters`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS area
    FROM qms_delivery_note
    WHERE tenant_code = BINARY 'customer-b' AND status = 'ACTIVE'
),
inbound_month AS (
    SELECT DATE_FORMAT(biz_date, '%Y-%m-01') AS month_start, SUM(area) AS inbound_area
    FROM inbound
    GROUP BY DATE_FORMAT(biz_date, '%Y-%m-01')
),
outbound_month AS (
    SELECT DATE_FORMAT(biz_date, '%Y-%m-01') AS month_start, SUM(area) AS outbound_area
    FROM outbound
    GROUP BY DATE_FORMAT(biz_date, '%Y-%m-01')
)
SELECT
    DATE_FORMAT(m.month_start, '%Y-%m') AS month,
    COALESCE(ROUND(i.inbound_area, 2), 0) AS area,
    '入库' AS `group`
FROM months m
LEFT JOIN inbound_month i ON i.month_start = DATE_FORMAT(m.month_start, '%Y-%m-01')
UNION ALL
SELECT
    DATE_FORMAT(m.month_start, '%Y-%m') AS month,
    COALESCE(ROUND(o.outbound_area, 2), 0) AS area,
    '出库' AS `group`
FROM months m
LEFT JOIN outbound_month o ON o.month_start = DATE_FORMAT(m.month_start, '%Y-%m-01')
ORDER BY month, `group`;

-- 组件：成品出库排名榜（面积）
WITH outbound AS (
    SELECT
        STR_TO_DATE(REPLACE(LEFT(TRIM(`erp_delivery_date`), 10), '/', '-'), '%Y-%m-%d') AS delivery_date,
        COALESCE(NULLIF(TRIM(`erp_shipment_part_no`), ''), NULLIF(TRIM(`erp_internal_product_no`), ''), NULLIF(TRIM(`erp_customer_part_no`), ''), '未维护产品') AS product_name,
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_issue_area_square_meters`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS area
    FROM qms_delivery_note
    WHERE tenant_code = BINARY 'customer-b' AND status = 'ACTIVE'
)
SELECT
    DENSE_RANK() OVER (ORDER BY SUM(area) DESC) AS 排名,
    product_name AS 产品,
    ROUND(SUM(area), 2) AS 出库面积
FROM outbound
WHERE YEAR(delivery_date) = YEAR(CURDATE())
GROUP BY product_name
ORDER BY 出库面积 DESC
LIMIT 10;

-- 组件：呆滞物料清单（超过 180 天未入库且仍有库存）
WITH material AS (
    SELECT
        NULLIF(TRIM(`erp_material_no`), '') AS 物料编号,
        NULLIF(TRIM(`erp_material_name`), '') AS 物料名称,
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_current_inventory`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS 库存数量,
        NULLIF(TRIM(`erp_unit`), '') AS 单位,
        STR_TO_DATE(REPLACE(LEFT(TRIM(`erp_inventory_latest_receipt_date`), 10), '/', '-'), '%Y-%m-%d') AS 最后入库日期
    FROM qms_material
    WHERE tenant_code = BINARY 'customer-b' AND status = 'ACTIVE'
)
SELECT
    ROW_NUMBER() OVER (ORDER BY 最后入库日期, 库存数量 DESC) AS 行号,
    物料编号, 物料名称, 库存数量, 单位, 最后入库日期,
    DATEDIFF(CURDATE(), 最后入库日期) AS 呆滞天数
FROM material
WHERE 库存数量 > 0
  AND 最后入库日期 < DATE_SUB(CURDATE(), INTERVAL 180 DAY)
ORDER BY 最后入库日期, 库存数量 DESC
LIMIT 100;

/* ========================================================================== */
/* 生产可视化数据                                                            */
/* ========================================================================== */

-- 组件：生产任务情况
SELECT
    ROW_NUMBER() OVER (ORDER BY material_input_date IS NULL, material_input_date, work_order_no) AS 行号,
    work_order_no AS 生产指令号,
    internal_product_no AS 厂内编号,
    COALESCE(customer_part_no, product_name, product_code) AS 客户料号,
    current_process_name AS 工艺,
    material AS 材质,
    planned_quantity AS 投料数量,
    status AS 状态,
    material_input_date AS 投料日期
FROM qms_work_order
WHERE tenant_code = BINARY 'customer-b'
  AND status = 'ACTIVE'
ORDER BY material_input_date IS NULL, material_input_date, work_order_no
LIMIT 100;

-- 组件：每日各工序产出面积（当前同步快照）
-- 注意：qms_process_output_summary 是按 source_key 幂等覆盖的当前快照，没有业务日期列；
-- 因此该表可展示“本次同步日”的工段产出，不能从现有表还原每日历史曲线。
SELECT
    DATE(updated_at) AS 统计日期,
    COALESCE(NULLIF(TRIM(`erp_process_section`), ''), '未维护工段') AS 工段,
    ROUND(SUM(CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_production_area`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4))), 2) AS 产出面积
FROM qms_process_output_summary
WHERE tenant_code = BINARY 'customer-b'
  AND status = 'ACTIVE'
GROUP BY DATE(updated_at), COALESCE(NULLIF(TRIM(`erp_process_section`), ''), '未维护工段')
ORDER BY 统计日期 DESC, 产出面积 DESC;

-- 组件：生产补料一览表
WITH replenishment AS (
    SELECT
        NULLIF(TRIM(`erp_material_replenishment_no`), '') AS replenish_no,
        NULLIF(TRIM(COALESCE(`erp_customer_part_no_replenishment_18b2446684`, `erp_customer_part_no_source_00e16c5278`)), '') AS customer_part_no,
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_material_replenishment_quantity`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS replenish_quantity,
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_material_replenishment_area`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS replenish_area,
        NULLIF(TRIM(`erp_original_order_no`), '') AS original_order_no,
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_original_order_placed_quantity`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS original_order_quantity,
        STR_TO_DATE(REPLACE(LEFT(TRIM(`erp_material_replenishment_date`), 10), '/', '-'), '%Y-%m-%d') AS replenish_date
    FROM qms_material_issue
    WHERE tenant_code = BINARY 'customer-b'
      AND status = 'ACTIVE'
      AND source_file LIKE '%补料资料%'
)
SELECT
    ROW_NUMBER() OVER (ORDER BY replenish_date DESC, replenish_no) AS 行号,
    replenish_no AS 补料编号,
    customer_part_no AS 客户料号,
    replenish_quantity AS 补料数量,
    replenish_area AS 补料面积,
    original_order_no AS 原订单编号,
    original_order_quantity AS 原下单数量,
    replenish_date AS 补料日期
FROM replenishment
ORDER BY replenish_date DESC, replenish_no
LIMIT 100;

-- 组件：每月成品生产面积（近 12 个月）
WITH RECURSIVE months AS (
    SELECT DATE_SUB(DATE_FORMAT(CURDATE(), '%Y-%m-01'), INTERVAL 11 MONTH) AS month_start
    UNION ALL
    SELECT DATE_ADD(month_start, INTERVAL 1 MONTH) FROM months
    WHERE month_start < DATE_FORMAT(CURDATE(), '%Y-%m-01')
),
receipt AS (
    SELECT
        STR_TO_DATE(REPLACE(LEFT(TRIM(`erp_receipt_date`), 10), '/', '-'), '%Y-%m-%d') AS receipt_date,
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_receipt_area_production`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS production_area
    FROM qms_finished_goods_receipt
    WHERE tenant_code = BINARY 'customer-b' AND status = 'ACTIVE'
)
SELECT DATE_FORMAT(m.month_start, '%Y-%m') AS 月份, COALESCE(ROUND(SUM(r.production_area), 2), 0) AS 成品生产面积
FROM months m
LEFT JOIN receipt r ON r.receipt_date >= m.month_start AND r.receipt_date < DATE_ADD(m.month_start, INTERVAL 1 MONTH)
GROUP BY m.month_start
ORDER BY m.month_start;

-- 组件：每月成品生产量（近 12 个月，单位：万）
WITH RECURSIVE months AS (
    SELECT DATE_SUB(DATE_FORMAT(CURDATE(), '%Y-%m-01'), INTERVAL 11 MONTH) AS month_start
    UNION ALL
    SELECT DATE_ADD(month_start, INTERVAL 1 MONTH) FROM months
    WHERE month_start < DATE_FORMAT(CURDATE(), '%Y-%m-01')
),
receipt AS (
    SELECT
        STR_TO_DATE(REPLACE(LEFT(TRIM(`erp_receipt_date`), 10), '/', '-'), '%Y-%m-%d') AS receipt_date,
        CAST(NULLIF(REGEXP_REPLACE(REPLACE(COALESCE(`erp_current_receipt_quantity`, ''), ',', ''), '[^0-9.-]', ''), '') AS DECIMAL(20, 4)) AS production_quantity
    FROM qms_finished_goods_receipt
    WHERE tenant_code = BINARY 'customer-b' AND status = 'ACTIVE'
)
SELECT DATE_FORMAT(m.month_start, '%Y-%m') AS 月份, COALESCE(ROUND(SUM(r.production_quantity) / 10000, 4), 0) AS 成品生产量_万
FROM months m
LEFT JOIN receipt r ON r.receipt_date >= m.month_start AND r.receipt_date < DATE_ADD(m.month_start, INTERVAL 1 MONTH)
GROUP BY m.month_start
ORDER BY m.month_start;

/* ========================================================================== */
/* 质量可视化数据                                                            */
/* ========================================================================== */

-- 质量口径：检验数量使用 QMS 当前业务口径，即优先采用批次计划数、否则工单计划数；
-- 良品数量 = 检验数量 - 不良数量。一个批次在不同工序的检验记录会分别计入各工序。

-- 组件：本月总检测数量
WITH inspection AS (
    SELECT
        ir.inspected_at,
        COALESCE(pb.planned_quantity, wo.planned_quantity, 0) AS inspection_quantity
    FROM qms_inspection_record ir
    JOIN qms_inspection_task it
      ON it.id = ir.task_id AND it.tenant_code = ir.tenant_code
    JOIN qms_work_order wo
      ON wo.id = it.work_order_id AND wo.tenant_code = it.tenant_code
    LEFT JOIN qms_production_batch pb
      ON pb.id = it.batch_id AND pb.tenant_code = it.tenant_code
    WHERE ir.tenant_code = BINARY 'customer-b'
)
SELECT
    COALESCE(SUM(CASE
        WHEN inspected_at >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
         AND inspected_at <  DATE_ADD(DATE_FORMAT(CURDATE(), '%Y-%m-01'), INTERVAL 1 MONTH)
        THEN inspection_quantity END), 0) AS 本月总检测数量
FROM inspection;

-- 组件：本月成品通过数量
WITH inspection AS (
    SELECT
        ir.inspected_at,
        COALESCE(pb.planned_quantity, wo.planned_quantity, 0) AS inspection_quantity,
        GREATEST(COALESCE(ir.defective_quantity, 0), 0) AS defective_quantity
    FROM qms_inspection_record ir
    JOIN qms_inspection_task it
      ON it.id = ir.task_id AND it.tenant_code = ir.tenant_code
    JOIN qms_work_order wo
      ON wo.id = it.work_order_id AND wo.tenant_code = it.tenant_code
    LEFT JOIN qms_production_batch pb
      ON pb.id = it.batch_id AND pb.tenant_code = it.tenant_code
    WHERE ir.tenant_code = BINARY 'customer-b'
)
SELECT
    COALESCE(SUM(CASE
        WHEN inspected_at >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
         AND inspected_at <  DATE_ADD(DATE_FORMAT(CURDATE(), '%Y-%m-01'), INTERVAL 1 MONTH)
        THEN GREATEST(inspection_quantity - defective_quantity, 0) END), 0) AS 本月成品通过数量
FROM inspection;

-- 组件：本月报废
WITH inspection AS (
    SELECT
        ir.inspected_at,
        GREATEST(COALESCE(ir.defective_quantity, 0), 0) AS defective_quantity
    FROM qms_inspection_record ir
    JOIN qms_inspection_task it
      ON it.id = ir.task_id AND it.tenant_code = ir.tenant_code
    JOIN qms_work_order wo
      ON wo.id = it.work_order_id AND wo.tenant_code = it.tenant_code
    LEFT JOIN qms_production_batch pb
      ON pb.id = it.batch_id AND pb.tenant_code = it.tenant_code
    WHERE ir.tenant_code = BINARY 'customer-b'
)
SELECT
    COALESCE(SUM(CASE
        WHEN inspected_at >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
         AND inspected_at <  DATE_ADD(DATE_FORMAT(CURDATE(), '%Y-%m-01'), INTERVAL 1 MONTH)
        THEN defective_quantity END), 0) AS 本月报废数量
FROM inspection;

-- 组件：本年报废
WITH inspection AS (
    SELECT
        ir.inspected_at,
        GREATEST(COALESCE(ir.defective_quantity, 0), 0) AS defective_quantity
    FROM qms_inspection_record ir
    JOIN qms_inspection_task it
      ON it.id = ir.task_id AND it.tenant_code = ir.tenant_code
    JOIN qms_work_order wo
      ON wo.id = it.work_order_id AND wo.tenant_code = it.tenant_code
    LEFT JOIN qms_production_batch pb
      ON pb.id = it.batch_id AND pb.tenant_code = it.tenant_code
    WHERE ir.tenant_code = BINARY 'customer-b'
)
SELECT
    COALESCE(SUM(CASE
        WHEN YEAR(inspected_at) = YEAR(CURDATE()) THEN defective_quantity END), 0) AS 本年报废数量
FROM inspection;

-- 组件：各工序合格量 / 合格率
WITH inspection AS (
    SELECT
        it.process_name,
        COALESCE(pb.planned_quantity, wo.planned_quantity, 0) AS inspection_quantity,
        GREATEST(COALESCE(ir.defective_quantity, 0), 0) AS defective_quantity
    FROM qms_inspection_record ir
    JOIN qms_inspection_task it ON it.id = ir.task_id AND it.tenant_code = ir.tenant_code
    JOIN qms_work_order wo ON wo.id = it.work_order_id AND wo.tenant_code = it.tenant_code
    LEFT JOIN qms_production_batch pb ON pb.id = it.batch_id AND pb.tenant_code = it.tenant_code
    WHERE ir.tenant_code = BINARY 'customer-b'
      AND ir.inspected_at >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
      AND ir.inspected_at <  DATE_ADD(DATE_FORMAT(CURDATE(), '%Y-%m-01'), INTERVAL 1 MONTH)
)
SELECT
    process_name AS 工序,
    SUM(inspection_quantity) AS 检测数量,
    SUM(GREATEST(inspection_quantity - defective_quantity, 0)) AS 合格数量,
    SUM(defective_quantity) AS 不良数量,
    ROUND(100 * SUM(GREATEST(inspection_quantity - defective_quantity, 0)) / NULLIF(SUM(inspection_quantity), 0), 2) AS 合格率_百分比
FROM inspection
GROUP BY process_name
ORDER BY 合格率_百分比 DESC, 检测数量 DESC;

-- 组件：本周每日检测数量趋势
WITH inspection AS (
    SELECT
        DATE(ir.inspected_at) AS inspection_date,
        COALESCE(pb.planned_quantity, wo.planned_quantity, 0) AS inspection_quantity
    FROM qms_inspection_record ir
    JOIN qms_inspection_task it ON it.id = ir.task_id AND it.tenant_code = ir.tenant_code
    JOIN qms_work_order wo ON wo.id = it.work_order_id AND wo.tenant_code = it.tenant_code
    LEFT JOIN qms_production_batch pb ON pb.id = it.batch_id AND pb.tenant_code = it.tenant_code
    WHERE ir.tenant_code = BINARY 'customer-b'
      AND DATE(ir.inspected_at) BETWEEN DATE_SUB(CURDATE(), INTERVAL 6 DAY) AND CURDATE()
)
SELECT inspection_date AS 日期, SUM(inspection_quantity) AS 检测数量
FROM inspection
GROUP BY inspection_date
ORDER BY inspection_date;

-- 组件：今日不良率趋势（按小时）
WITH inspection AS (
    SELECT
        HOUR(ir.inspected_at) AS hour_no,
        COALESCE(pb.planned_quantity, wo.planned_quantity, 0) AS inspection_quantity,
        GREATEST(COALESCE(ir.defective_quantity, 0), 0) AS defective_quantity
    FROM qms_inspection_record ir
    JOIN qms_inspection_task it ON it.id = ir.task_id AND it.tenant_code = ir.tenant_code
    JOIN qms_work_order wo ON wo.id = it.work_order_id AND wo.tenant_code = it.tenant_code
    LEFT JOIN qms_production_batch pb ON pb.id = it.batch_id AND pb.tenant_code = it.tenant_code
    WHERE ir.tenant_code = BINARY 'customer-b'
      AND DATE(ir.inspected_at) = CURDATE()
)
SELECT
    CONCAT(LPAD(hour_no, 2, '0'), ':00') AS 时段,
    SUM(inspection_quantity) AS 检测数量,
    SUM(defective_quantity) AS 不良数量,
    ROUND(100 * SUM(defective_quantity) / NULLIF(SUM(inspection_quantity), 0), 2) AS 不良率_百分比
FROM inspection
GROUP BY hour_no
ORDER BY hour_no;

-- 组件：本月缺陷类型分布（环形图）
WITH defects AS (
    SELECT
        COALESCE(NULLIF(TRIM(ir.defect_summary), ''), '未填写缺陷说明') AS defect_type,
        GREATEST(COALESCE(ir.defective_quantity, 0), 0) AS defective_quantity
    FROM qms_inspection_record ir
    WHERE ir.tenant_code = BINARY 'customer-b'
      AND ir.verdict = 'FAIL'
      AND ir.inspected_at >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
      AND ir.inspected_at <  DATE_ADD(DATE_FORMAT(CURDATE(), '%Y-%m-01'), INTERVAL 1 MONTH)
)
SELECT defect_type AS name, SUM(defective_quantity) AS value
FROM defects
GROUP BY defect_type
ORDER BY value DESC
LIMIT 10;

-- 组件：本周每日报废数量
SELECT
    DATE(inspected_at) AS 日期,
    SUM(GREATEST(COALESCE(defective_quantity, 0), 0)) AS 报废数量
FROM qms_inspection_record
WHERE tenant_code = BINARY 'customer-b'
  AND DATE(inspected_at) BETWEEN DATE_SUB(CURDATE(), INTERVAL 6 DAY) AND CURDATE()
GROUP BY DATE(inspected_at)
ORDER BY 日期;

-- 组件：产品缺陷信息表
WITH defects AS (
    SELECT
        ir.inspected_at,
        it.process_name,
        wo.work_order_no,
        COALESCE(wo.customer_part_no, wo.product_name, wo.product_code) AS product_name,
        COALESCE(pb.planned_quantity, wo.planned_quantity, 0) AS inspection_quantity,
        GREATEST(COALESCE(ir.defective_quantity, 0), 0) AS defective_quantity,
        COALESCE(NULLIF(TRIM(ir.defect_summary), ''), '未填写缺陷说明') AS defect_summary
    FROM qms_inspection_record ir
    JOIN qms_inspection_task it ON it.id = ir.task_id AND it.tenant_code = ir.tenant_code
    JOIN qms_work_order wo ON wo.id = it.work_order_id AND wo.tenant_code = it.tenant_code
    LEFT JOIN qms_production_batch pb ON pb.id = it.batch_id AND pb.tenant_code = it.tenant_code
    WHERE ir.tenant_code = BINARY 'customer-b'
      AND ir.verdict = 'FAIL'
)
SELECT
    ROW_NUMBER() OVER (ORDER BY inspected_at DESC) AS 行号,
    product_name AS 产品名称,
    work_order_no AS 生产指令号,
    process_name AS 工序,
    inspection_quantity AS 检测数量,
    defective_quantity AS 不良总数,
    defect_summary AS 缺陷说明,
    inspected_at AS 测试时间
FROM defects
ORDER BY inspected_at DESC
LIMIT 100;
