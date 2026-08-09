-- Query 04: Customers Who Placed Orders but Never Had Any Item Delivered
SELECT 
    c.customer_id,
    c.customer_name,
    c.email,
    COUNT(o.order_id) AS total_orders_placed
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name, c.email
HAVING SUM(CASE WHEN o.status = 'DELIVERED' THEN 1 ELSE 0 END) = 0
ORDER BY total_orders_placed DESC;
