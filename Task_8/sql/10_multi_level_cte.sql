-- Query 10: Multi-Level CTE for Monthly Customer Segmentation
WITH monthly_customer_revenue AS (
    SELECT 
        o.customer_id,
        strftime('%Y-%m', o.order_date) AS month,
        SUM(oi.quantity * oi.unit_price * (1.0 - oi.discount_percent / 100.0)) AS revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.customer_id IS NOT NULL AND o.status != 'CANCELLED'
    GROUP BY o.customer_id, strftime('%Y-%m', o.order_date)
),
customer_segments AS (
    SELECT 
        customer_id,
        month,
        revenue,
        CASE 
            WHEN revenue > 10000 THEN 'High'
            WHEN revenue BETWEEN 5000 AND 10000 THEN 'Medium'
            ELSE 'Low'
        END AS segment
    FROM monthly_customer_revenue
)
SELECT 
    month,
    segment,
    COUNT(customer_id) AS customer_count,
    ROUND(SUM(revenue), 2) AS total_segment_revenue
FROM customer_segments
GROUP BY month, segment
ORDER BY month ASC, 
    CASE segment 
        WHEN 'High' THEN 1 
        WHEN 'Medium' THEN 2 
        WHEN 'Low' THEN 3 
    END;
