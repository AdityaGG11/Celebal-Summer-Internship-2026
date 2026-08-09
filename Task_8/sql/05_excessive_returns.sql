-- Query 05: Products with Excessive Returns (Returned Items > Purchased Items)
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    SUM(CASE WHEN oi.quantity > 0 THEN oi.quantity ELSE 0 END) AS total_purchased_qty,
    SUM(CASE WHEN oi.quantity < 0 THEN ABS(oi.quantity) ELSE 0 END) AS total_returned_qty
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_id, p.product_name, p.category
HAVING total_returned_qty > total_purchased_qty
ORDER BY (total_returned_qty - total_purchased_qty) DESC;
