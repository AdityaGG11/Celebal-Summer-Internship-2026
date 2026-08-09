-- Query 13: Customer First vs Last Purchased Category Shift Analysis
WITH customer_category_orders AS (
    SELECT 
        o.customer_id,
        p.category,
        o.order_date,
        ROW_NUMBER() OVER (PARTITION BY o.customer_id ORDER BY o.order_date ASC, oi.item_id ASC) AS seq_first,
        ROW_NUMBER() OVER (PARTITION BY o.customer_id ORDER BY o.order_date DESC, oi.item_id DESC) AS seq_last
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    WHERE o.customer_id IS NOT NULL AND o.status != 'CANCELLED'
),
first_categories AS (
    SELECT customer_id, category AS first_category
    FROM customer_category_orders
    WHERE seq_first = 1
),
last_categories AS (
    SELECT customer_id, category AS last_category
    FROM customer_category_orders
    WHERE seq_last = 1
)
SELECT 
    f.customer_id,
    f.first_category,
    l.last_category,
    CASE 
        WHEN f.first_category != l.last_category THEN 'Yes' 
        ELSE 'No' 
    END AS category_shift
FROM first_categories f
JOIN last_categories l ON f.customer_id = l.customer_id
ORDER BY f.customer_id;
