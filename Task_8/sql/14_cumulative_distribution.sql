-- Query 14: Cumulative Distribution & Revenue Concentration
WITH customer_revenue AS (
    SELECT 
        o.customer_id,
        ROUND(SUM(oi.quantity * oi.unit_price * (1.0 - oi.discount_percent / 100.0)), 2) AS revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.customer_id IS NOT NULL AND o.status != 'CANCELLED'
    GROUP BY o.customer_id
),
total_rev AS (
    SELECT SUM(revenue) AS total_system_revenue FROM customer_revenue
),
ordered_revenue AS (
    SELECT 
        customer_id,
        revenue,
        SUM(revenue) OVER (ORDER BY revenue DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_revenue,
        (SELECT total_system_revenue FROM total_rev) AS grand_total
    FROM customer_revenue
)
SELECT 
    customer_id,
    revenue,
    ROUND(cumulative_revenue, 2) AS cumulative_revenue,
    ROUND((cumulative_revenue * 100.0) / grand_total, 2) AS cumulative_percent
FROM ordered_revenue
ORDER BY revenue DESC;
