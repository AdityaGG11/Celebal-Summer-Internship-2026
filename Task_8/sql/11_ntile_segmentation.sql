-- Query 11: NTILE Customer LTV Quartile Segmentation
WITH customer_ltv AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        ROUND(SUM(oi.quantity * oi.unit_price * (1.0 - oi.discount_percent / 100.0)), 2) AS total_value
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.status != 'CANCELLED'
    GROUP BY c.customer_id, c.customer_name
),
quartiled_customers AS (
    SELECT 
        customer_id,
        customer_name,
        total_value,
        NTILE(4) OVER (ORDER BY total_value DESC) AS quartile
    FROM customer_ltv
)
SELECT 
    customer_id,
    customer_name,
    total_value,
    quartile,
    CASE quartile
        WHEN 1 THEN 'Platinum'
        WHEN 2 THEN 'Gold'
        WHEN 3 THEN 'Silver'
        WHEN 4 THEN 'Bronze'
    END AS quartile_label
FROM quartiled_customers
ORDER BY total_value DESC;
