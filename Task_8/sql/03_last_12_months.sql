-- Query 03: Month-wise Order Count for Last 12 Months in Dataset
WITH max_date AS (
    SELECT MAX(order_date) AS latest_date FROM orders
),
monthly_orders AS (
    SELECT 
        strftime('%Y-%m', order_date) AS month,
        COUNT(order_id) AS order_count,
        COUNT(DISTINCT customer_id) AS unique_customers
    FROM orders
    WHERE order_date >= (SELECT date(latest_date, 'start of month', '-11 months') FROM max_date)
    GROUP BY strftime('%Y-%m', order_date)
)
SELECT month, order_count, unique_customers
FROM monthly_orders
ORDER BY month ASC;
