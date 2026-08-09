-- Query 15: Cohort Analysis by Registration Month
WITH customer_cohorts AS (
    SELECT 
        customer_id,
        strftime('%Y-%m', registration_date) AS cohort_month
    FROM customers
),
customer_orders AS (
    SELECT DISTINCT
        o.customer_id,
        CAST((
            (strftime('%Y', o.order_date) - strftime('%Y', c.registration_date)) * 12 +
            (strftime('%m', o.order_date) - strftime('%m', c.registration_date))
        ) AS INTEGER) AS month_offset
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.status != 'CANCELLED'
),
cohort_sizes AS (
    SELECT cohort_month, COUNT(customer_id) AS total_customers
    FROM customer_cohorts
    GROUP BY cohort_month
)
SELECT 
    cs.cohort_month,
    cs.total_customers AS cohort_size,
    COUNT(DISTINCT CASE WHEN co.month_offset = 0 THEN cc.customer_id END) AS month_0_active,
    COUNT(DISTINCT CASE WHEN co.month_offset = 1 THEN cc.customer_id END) AS month_1_active,
    COUNT(DISTINCT CASE WHEN co.month_offset = 2 THEN cc.customer_id END) AS month_2_active,
    COUNT(DISTINCT CASE WHEN co.month_offset = 3 THEN cc.customer_id END) AS month_3_active,
    ROUND(COUNT(DISTINCT CASE WHEN co.month_offset = 1 THEN cc.customer_id END) * 100.0 / cs.total_customers, 2) AS month_1_retention_pct
FROM cohort_sizes cs
JOIN customer_cohorts cc ON cs.cohort_month = cc.cohort_month
LEFT JOIN customer_orders co ON cc.customer_id = co.customer_id
GROUP BY cs.cohort_month, cs.total_customers
ORDER BY cs.cohort_month ASC;
