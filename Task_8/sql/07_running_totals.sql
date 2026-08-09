-- Query 07: Running Totals of Daily Revenue per Region
WITH daily_region_revenue AS (
    SELECT 
        o.region_code,
        DATE(o.order_date) AS order_date,
        ROUND(SUM(oi.quantity * oi.unit_price * (1.0 - oi.discount_percent / 100.0)), 2) AS daily_revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.status != 'CANCELLED'
    GROUP BY o.region_code, DATE(o.order_date)
)
SELECT 
    region_code,
    order_date,
    daily_revenue,
    ROUND(SUM(daily_revenue) OVER (
        PARTITION BY region_code 
        ORDER BY order_date 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ), 2) AS running_total
FROM daily_region_revenue
ORDER BY region_code, order_date;
