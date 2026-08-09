-- Query 12: Year-over-Year (YoY) Revenue Comparison
WITH monthly_revenue AS (
    SELECT 
        CAST(strftime('%Y', o.order_date) AS INTEGER) AS year,
        CAST(strftime('%m', o.order_date) AS INTEGER) AS month_num,
        strftime('%Y-%m', o.order_date) AS year_month,
        ROUND(SUM(oi.quantity * oi.unit_price * (1.0 - oi.discount_percent / 100.0)), 2) AS revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.status != 'CANCELLED'
    GROUP BY strftime('%Y-%m', o.order_date)
)
SELECT 
    cur.year,
    cur.month_num AS month,
    cur.revenue,
    prev.revenue AS prev_year_revenue,
    CASE 
        WHEN prev.revenue IS NULL OR prev.revenue = 0 THEN NULL
        ELSE ROUND(((cur.revenue - prev.revenue) * 100.0) / prev.revenue, 2)
    END AS yoy_growth_percent
FROM monthly_revenue cur
LEFT JOIN monthly_revenue prev 
    ON cur.year = prev.year + 1 AND cur.month_num = prev.month_num
ORDER BY cur.year ASC, cur.month_num ASC;
