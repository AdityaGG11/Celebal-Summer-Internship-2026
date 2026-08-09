-- Query 06: Category Return Rate
SELECT 
    p.category,
    SUM(CASE WHEN oi.quantity > 0 THEN oi.quantity ELSE 0 END) AS total_purchased_items,
    SUM(CASE WHEN oi.quantity < 0 THEN ABS(oi.quantity) ELSE 0 END) AS total_returned_items,
    ROUND(
        (SUM(CASE WHEN oi.quantity < 0 THEN ABS(oi.quantity) ELSE 0 END) * 100.0) /
        NULLIF(SUM(CASE WHEN oi.quantity > 0 THEN oi.quantity ELSE 0 END), 0),
        2
    ) AS return_rate_percent
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.category
ORDER BY return_rate_percent DESC;
