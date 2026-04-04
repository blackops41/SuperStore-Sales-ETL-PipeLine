-- ============================================================
-- BUSINESS QUERIES — Superstore Data Warehouse
-- Layer: SQL (Business Queries)
-- Stack: ETL (Python) → MySQL (DWH) → SQL → BI / Python
-- ============================================================


-- ------------------------------------------------------------
-- 1. EXECUTIVE SUMMARY — Total Sales / Profit / Margin
-- ------------------------------------------------------------
SELECT 
    ROUND(SUM(Sales), 2) AS total_sales,
    ROUND(SUM(Profit), 2) AS total_profit,
    ROUND(SUM(Profit) / NULLIF(SUM(Sales), 0) * 100, 2) AS margin_pct
FROM superstore_orders;


-- ------------------------------------------------------------
-- 2. MONTHLY SALES TREND
-- ------------------------------------------------------------
SELECT 
    DATE_FORMAT(Order_Date, '%Y-%m') AS month,
    ROUND(SUM(Sales), 2) AS total_sales,
    ROUND(SUM(Profit), 2) AS total_profit
FROM superstore_orders
GROUP BY month
ORDER BY month;


-- ------------------------------------------------------------
-- 3. YEAR-OVER-YEAR (YoY) GROWTH  [FIXED WITH CTE]
-- ------------------------------------------------------------
WITH yearly_sales AS (
    SELECT 
        YEAR(Order_Date) AS year,
        SUM(Sales) AS total_sales
    FROM superstore_orders
    GROUP BY YEAR(Order_Date)
)
SELECT 
    year,
    ROUND(total_sales, 2) AS total_sales,
    ROUND(total_sales - LAG(total_sales) OVER (ORDER BY year), 2) AS yoy_diff,
    ROUND(
        (total_sales - LAG(total_sales) OVER (ORDER BY year)) 
        / NULLIF(LAG(total_sales) OVER (ORDER BY year), 0) * 100
    , 2) AS yoy_growth_pct
FROM yearly_sales
ORDER BY year;


-- ------------------------------------------------------------
-- 4. PARETO — Top customers contributing to ~80% of sales
-- ------------------------------------------------------------
SELECT *
FROM (
    SELECT 
        Customer_Name,
        ROUND(SUM(Sales), 2) AS total_sales,
        ROUND(SUM(Sales) / SUM(SUM(Sales)) OVER () * 100, 2) AS pct_of_total,
        ROUND(
            SUM(SUM(Sales)) OVER (ORDER BY SUM(Sales) DESC)
            / SUM(SUM(Sales)) OVER () * 100
        , 2) AS cumulative_pct
    FROM superstore_orders
    GROUP BY Customer_Name
) t
WHERE cumulative_pct <= 85   -- 80% Pareto band (business tolerance)
ORDER BY total_sales DESC;


-- ------------------------------------------------------------
-- 5. SEGMENT ANALYSIS — Only significant segments (>100K Sales)
-- ------------------------------------------------------------
SELECT 
    Category,
    Region,
    ROUND(SUM(Sales), 2) AS total_sales,
    ROUND(SUM(Profit), 2) AS total_profit,
    ROUND(SUM(Profit) / NULLIF(SUM(Sales), 0) * 100, 2) AS margin_pct
FROM superstore_orders
GROUP BY Category, Region
HAVING SUM(Sales) > 100000
ORDER BY total_sales DESC;


-- ------------------------------------------------------------
-- 6. REGION PERFORMANCE — Corrected KPI (order-level avg profit)
-- ------------------------------------------------------------
SELECT 
    Region,
    COUNT(DISTINCT Order_ID) AS order_count,
    ROUND(SUM(Sales), 2) AS total_sales,
    ROUND(SUM(Profit), 2) AS total_profit,
    ROUND(SUM(Profit) / COUNT(DISTINCT Order_ID), 2) AS avg_profit_per_order
FROM superstore_orders
GROUP BY Region
ORDER BY total_sales DESC;


-- ------------------------------------------------------------
-- 7. SUB-CATEGORY MARGIN ANALYSIS — Negative margin detection
-- ------------------------------------------------------------
SELECT 
    Sub_Category,
    ROUND(SUM(Sales), 2) AS total_sales,
    ROUND(SUM(Profit), 2) AS total_profit,
    ROUND(SUM(Profit) / NULLIF(SUM(Sales), 0) * 100, 2) AS margin_pct
FROM superstore_orders
GROUP BY Sub_Category
HAVING SUM(Profit) / NULLIF(SUM(Sales), 0) < 0
ORDER BY margin_pct ASC;


-- ------------------------------------------------------------
-- 8. DISCOUNT IMPACT — Profit erosion analysis
-- ------------------------------------------------------------
SELECT 
    Discount,
    COUNT(*) AS order_count,
    ROUND(SUM(Sales), 2) AS total_sales,
    ROUND(SUM(Profit), 2) AS total_profit,
    ROUND(AVG(Profit), 2) AS avg_profit
FROM superstore_orders
GROUP BY Discount
ORDER BY Discount;


-- ------------------------------------------------------------
-- 9. LOSS-MAKING SEGMENTS — Critical risk detection
-- ------------------------------------------------------------
SELECT 
    Category,
    Region,
    ROUND(SUM(Sales), 2) AS total_sales,
    ROUND(SUM(Profit), 2) AS total_profit
FROM superstore_orders
GROUP BY Category, Region
HAVING SUM(Profit) < 0
ORDER BY total_profit ASC;
