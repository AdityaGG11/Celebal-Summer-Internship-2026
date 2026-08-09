-- Query 09: Customer Order Gap Analysis (LAG) and 'At Risk' Flagging
WITH customer_orders AS (
    SELECT DISTINCT
        customer_id,
        order_date,
        LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) AS previous_order_date
    FROM orders
    WHERE customer_id IS NOT NULL AND status != 'CANCELLED'
),
order_gaps AS (
    SELECT 
        customer_id,
        order_date,
        previous_order_date,
        ROUND(JULIANDAY(order_date) - JULIANDAY(previous_order_date), 1) AS days_gap
    FROM customer_orders
),
customer_avg_gaps AS (
    SELECT 
        customer_id,
        COUNT(order_date) AS total_orders,
        ROUND(AVG(days_gap), 1) AS avg_days_gap
    FROM order_gaps
    WHERE days_gap IS NOT NULL
    GROUP BY customer_id
)
SELECT 
    og.customer_id,
    og.order_date,
    og.previous_order_date,
    og.days_gap,
    ag.avg_days_gap,
    CASE 
        WHEN ag.avg_days_gap > 30 THEN 'At Risk' 
        ELSE 'Active' 
    END AS customer_status
FROM order_gaps og
JOIN customer_avg_gaps ag ON og.customer_id = ag.customer_id
ORDER BY og.customer_id, og.order_date;
