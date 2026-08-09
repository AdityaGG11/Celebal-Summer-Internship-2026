-- Query 08: Dense Rank of Products by Revenue in Each Category
WITH product_revenue AS (
    SELECT 
        p.category,
        p.product_id,
        p.product_name,
        ROUND(SUM(oi.quantity * oi.unit_price * (1.0 - oi.discount_percent / 100.0)), 2) AS total_revenue
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.status != 'CANCELLED'
    GROUP BY p.category, p.product_id, p.product_name
)
SELECT 
    category,
    product_name,
    total_revenue,
    DENSE_RANK() OVER (
        PARTITION BY category 
        ORDER BY total_revenue DESC
    ) AS rank_in_category
FROM product_revenue
ORDER BY category, rank_in_category;
