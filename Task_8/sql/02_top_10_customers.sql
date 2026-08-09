-- Query 02: Top 10 Customers by Total Order Value
SELECT 
    c.customer_id,
    c.customer_name,
    c.email,
    c.customer_type,
    ROUND(SUM(oi.quantity * oi.unit_price * (1.0 - oi.discount_percent / 100.0)), 2) AS total_order_value
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status != 'CANCELLED'
GROUP BY c.customer_id, c.customer_name, c.email, c.customer_type
ORDER BY total_order_value DESC
LIMIT 10;
