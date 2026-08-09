-- Query 16: Self-Join combined with Window Functions for Order Sequence & Reorder Interval Analysis
WITH customer_order_details AS (
    SELECT 
        o.order_id,
        o.customer_id,
        o.order_date,
        SUM(oi.quantity * oi.unit_price * (1.0 - oi.discount_percent / 100.0)) AS order_value,
        ROW_NUMBER() OVER (PARTITION BY o.customer_id ORDER BY o.order_date) AS order_seq
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.customer_id IS NOT NULL AND o.status != 'CANCELLED'
    GROUP BY o.order_id, o.customer_id, o.order_date
)
SELECT 
    curr.customer_id,
    curr.order_id AS current_order_id,
    curr.order_date AS current_order_date,
    ROUND(curr.order_value, 2) AS current_order_value,
    prev.order_id AS previous_order_id,
    prev.order_date AS previous_order_date,
    ROUND(prev.order_value, 2) AS previous_order_value,
    ROUND(JULIANDAY(curr.order_date) - JULIANDAY(prev.order_date), 1) AS days_since_prev_order,
    ROUND(curr.order_value - prev.order_value, 2) AS order_value_diff
FROM customer_order_details curr
JOIN customer_order_details prev 
    ON curr.customer_id = prev.customer_id 
   AND curr.order_seq = prev.order_seq + 1
ORDER BY curr.customer_id, curr.order_seq;
