-- Query 17: Frequently Bought Together Product Pairs
SELECT 
    p1.product_name AS product_a,
    p2.product_name AS product_b,
    COUNT(DISTINCT oi1.order_id) AS times_bought_together
FROM order_items oi1
JOIN order_items oi2 ON oi1.order_id = oi2.order_id AND oi1.product_id < oi2.product_id
JOIN products p1 ON oi1.product_id = p1.product_id
JOIN products p2 ON oi2.product_id = p2.product_id
JOIN orders o ON oi1.order_id = o.order_id
WHERE o.status != 'CANCELLED'
GROUP BY oi1.product_id, oi2.product_id, p1.product_name, p2.product_name
ORDER BY times_bought_together DESC, product_a ASC, product_b ASC
LIMIT 20;
