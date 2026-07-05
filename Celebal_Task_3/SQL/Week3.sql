-- ==========================================================
-- CELEBAL TECHNOLOGIES SUMMER INTERNSHIP 2026
-- WEEK 3 : ADVANCED SQL USING SUBQUERIES, CTEs & WINDOW FUNCTIONS
-- DATASET : SUPERSTORE
-- AUTHOR : Aditya Kumar
-- ==========================================================


-- ==========================================================
-- DATABASE SETUP
-- ==========================================================

CREATE DATABASE celebal_task3;

USE celebal_task3;


-- ==========================================================
-- DATASET VERIFICATION
-- ==========================================================

SHOW TABLES;

DESCRIBE superstore_raw;

SELECT * FROM superstore_raw LIMIT 5;

SELECT COUNT(*) AS total_records FROM superstore_raw;


-- ==========================================================
-- CREATE NORMALIZED TABLES
-- ==========================================================

CREATE TABLE customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    customer_name VARCHAR(100),
    segment VARCHAR(50),
    country VARCHAR(50),
    city VARCHAR(50),
    state VARCHAR(50),
    postal_code INT,
    region VARCHAR(50)
);

CREATE TABLE orders (
    order_id VARCHAR(20) PRIMARY KEY,
    order_date VARCHAR(20),
    ship_date VARCHAR(20),
    ship_mode VARCHAR(50),
    customer_id VARCHAR(20),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE products (
    product_id VARCHAR(30) PRIMARY KEY,
    category VARCHAR(50),
    sub_category VARCHAR(50),
    product_name VARCHAR(150),
    sales DOUBLE,
    quantity INT,
    discount DOUBLE,
    profit DOUBLE
);


-- ==========================================================
-- VERIFY CREATED TABLES
-- ==========================================================

SHOW TABLES;

DESCRIBE customers;

DESCRIBE orders;

DESCRIBE products;


-- ==========================================================
-- INSERT DATA INTO CUSTOMERS TABLE
-- ==========================================================

INSERT INTO customers (customer_id, customer_name, segment, country, city, state, postal_code, region)
SELECT `Customer ID`, MAX(`Customer Name`), MAX(Segment), MAX(Country), MAX(City), MAX(State), MAX(`Postal Code`), MAX(Region)
FROM superstore_raw
GROUP BY `Customer ID`;

SELECT COUNT(*) AS total_customers FROM customers;

SELECT * FROM customers LIMIT 5;


-- ==========================================================
-- INSERT DATA INTO ORDERS TABLE
-- ==========================================================

INSERT INTO orders (order_id, order_date, ship_date, ship_mode, customer_id)
SELECT `Order ID`, MAX(`Order Date`), MAX(`Ship Date`), MAX(`Ship Mode`), MAX(`Customer ID`)
FROM superstore_raw
GROUP BY `Order ID`;

SELECT COUNT(*) AS total_orders FROM orders;

SELECT * FROM orders LIMIT 5;


-- ==========================================================
-- INSERT DATA INTO PRODUCTS TABLE
-- ==========================================================

INSERT INTO products (product_id, category, sub_category, product_name, sales, quantity, discount, profit)
SELECT `Product ID`, MAX(Category), MAX(`Sub-Category`), MAX(`Product Name`), MAX(Sales), MAX(Quantity), MAX(Discount), MAX(Profit)
FROM superstore_raw
GROUP BY `Product ID`;

SELECT COUNT(*) AS total_products FROM products;

SELECT * FROM products LIMIT 5;


-- ==========================================================
-- Q1 : ORDERS WITH SALES GREATER THAN AVERAGE SALES (SUBQUERY)
-- ==========================================================

SELECT * FROM superstore_raw
WHERE Sales > (SELECT AVG(Sales) FROM superstore_raw);


-- ==========================================================
-- Q2 : HIGHEST SALES ORDER FOR EACH CUSTOMER (SUBQUERY)
-- ==========================================================

SELECT s.`Customer ID`, s.`Customer Name`, s.`Order ID`, s.Sales
FROM superstore_raw s
JOIN (
    SELECT `Customer ID`, MAX(Sales) AS max_sales
    FROM superstore_raw
    GROUP BY `Customer ID`
) m
ON s.`Customer ID` = m.`Customer ID`
AND s.Sales = m.max_sales;


-- ==========================================================
-- Q3 : TOTAL SALES FOR EACH CUSTOMER (CTE)
-- ==========================================================

WITH customer_sales AS (
    SELECT `Customer ID`, `Customer Name`, SUM(Sales) AS total_sales
    FROM superstore_raw
    GROUP BY `Customer ID`, `Customer Name`
)
SELECT *
FROM customer_sales
ORDER BY total_sales DESC;


-- ==========================================================
-- Q4 : CUSTOMERS WITH ABOVE AVERAGE TOTAL SALES (CTE + SUBQUERY)
-- ==========================================================

WITH customer_sales AS (
    SELECT `Customer ID`, `Customer Name`, ROUND(SUM(Sales),2) AS total_sales
    FROM superstore_raw
    GROUP BY `Customer ID`, `Customer Name`
)
SELECT *
FROM customer_sales
WHERE total_sales > (SELECT AVG(total_sales) FROM customer_sales)
ORDER BY total_sales DESC;


-- ==========================================================
-- Q5 : RANK CUSTOMERS BASED ON TOTAL SALES (WINDOW FUNCTION)
-- ==========================================================

WITH customer_sales AS (
    SELECT `Customer ID`, `Customer Name`, ROUND(SUM(Sales),2) AS total_sales
    FROM superstore_raw
    GROUP BY `Customer ID`, `Customer Name`
)
SELECT `Customer ID`, `Customer Name`, total_sales,
RANK() OVER (ORDER BY total_sales DESC) AS customer_rank
FROM customer_sales;


-- ==========================================================
-- Q6 : ASSIGN ROW NUMBER TO ORDERS WITHIN EACH CUSTOMER
-- ==========================================================

SELECT `Customer ID`, `Customer Name`, `Order ID`, Sales,
ROW_NUMBER() OVER (PARTITION BY `Customer ID` ORDER BY Sales DESC) AS row_num
FROM superstore_raw;


-- ==========================================================
-- Q7 : DISPLAY TOP 3 CUSTOMERS USING WINDOW FUNCTION
-- ==========================================================

WITH customer_sales AS (
    SELECT `Customer ID`, `Customer Name`, ROUND(SUM(Sales),2) AS total_sales
    FROM superstore_raw
    GROUP BY `Customer ID`, `Customer Name`
),
ranked_customers AS (
    SELECT *, RANK() OVER (ORDER BY total_sales DESC) AS customer_rank
    FROM customer_sales
)
SELECT *
FROM ranked_customers
WHERE customer_rank <= 3;


-- ==========================================================
-- Q8 : CUSTOMER SALES RANKING USING JOIN + CTE + WINDOW FUNCTION
-- ==========================================================

WITH customer_sales AS (
    SELECT `Customer ID`, ROUND(SUM(Sales),2) AS total_sales
    FROM superstore_raw
    GROUP BY `Customer ID`
)
SELECT c.customer_id, c.customer_name, cs.total_sales,
RANK() OVER (ORDER BY cs.total_sales DESC) AS customer_rank
FROM customer_sales cs
JOIN customers c
ON cs.`Customer ID` = c.customer_id
ORDER BY customer_rank;


-- ==========================================================
-- MINI PROJECT 1 : TOP 5 CUSTOMERS
-- ==========================================================

SELECT `Customer ID`, `Customer Name`, ROUND(SUM(Sales),2) AS total_sales
FROM superstore_raw
GROUP BY `Customer ID`, `Customer Name`
ORDER BY total_sales DESC
LIMIT 5;


-- ==========================================================
-- MINI PROJECT 2 : BOTTOM 5 CUSTOMERS
-- ==========================================================

SELECT `Customer ID`, `Customer Name`, ROUND(SUM(Sales),2) AS total_sales
FROM superstore_raw
GROUP BY `Customer ID`, `Customer Name`
ORDER BY total_sales ASC
LIMIT 5;


-- ==========================================================
-- MINI PROJECT 3 : CUSTOMERS WITH ONLY ONE ORDER
-- ==========================================================

SELECT `Customer ID`, `Customer Name`, COUNT(DISTINCT `Order ID`) AS total_orders
FROM superstore_raw
GROUP BY `Customer ID`, `Customer Name`
HAVING COUNT(DISTINCT `Order ID`) = 1;


-- ==========================================================
-- MINI PROJECT 4 : CUSTOMERS WITH ABOVE AVERAGE SALES
-- ==========================================================

WITH customer_sales AS (
    SELECT `Customer ID`, `Customer Name`, ROUND(SUM(Sales),2) AS total_sales
    FROM superstore_raw
    GROUP BY `Customer ID`, `Customer Name`
)
SELECT *
FROM customer_sales
WHERE total_sales > (SELECT AVG(total_sales) FROM customer_sales)
ORDER BY total_sales DESC;


-- ==========================================================
-- MINI PROJECT 5 : HIGHEST ORDER VALUE FOR EACH CUSTOMER
-- ==========================================================

SELECT s.`Customer ID`, s.`Customer Name`, s.`Order ID`, s.Sales
FROM superstore_raw s
JOIN (
    SELECT `Customer ID`, MAX(Sales) AS max_sales
    FROM superstore_raw
    GROUP BY `Customer ID`
) m
ON s.`Customer ID` = m.`Customer ID`
AND s.Sales = m.max_sales
ORDER BY s.Sales DESC;