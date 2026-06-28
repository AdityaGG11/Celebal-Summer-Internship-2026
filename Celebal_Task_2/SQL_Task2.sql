-- ============================================================
-- Celebal Summer Internship 2026
-- Week 2 - SQL Assignment
-- Name: Aditya Kumar
-- Description: E-Commerce Sales Database
-- ============================================================

-- ============================================================
-- STEP 1: Create Database
-- ============================================================

CREATE DATABASE celebal_task2;
USE celebal_task2;

-- ============================================================
-- STEP 2: Create customers Table
-- ============================================================

CREATE TABLE customers (
    customer_id   INT PRIMARY KEY,
    first_name    VARCHAR(50) NOT NULL,
    last_name     VARCHAR(50) NOT NULL,
    email         VARCHAR(100) UNIQUE NOT NULL,
    city          VARCHAR(50) NOT NULL,
    state         VARCHAR(50) NOT NULL,
    join_date     DATE NOT NULL,
    is_premium    BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_customers_city
ON customers(city);

CREATE INDEX idx_customers_state
ON customers(state);

-- ============================================================
-- STEP 3: Create products Table
-- ============================================================

CREATE TABLE products (
    product_id    INT PRIMARY KEY,
    product_name  VARCHAR(100) NOT NULL,
    category      VARCHAR(50) NOT NULL,
    brand         VARCHAR(50) NOT NULL,
    unit_price    DECIMAL(10,2) NOT NULL CHECK(unit_price > 0),
    stock_qty     INT NOT NULL DEFAULT 0 CHECK(stock_qty >= 0)
);

CREATE INDEX idx_products_category
ON products(category);

-- ============================================================
-- STEP 4: Create orders Table
-- ============================================================

CREATE TABLE orders (
    order_id      INT PRIMARY KEY,
    customer_id   INT NOT NULL,
    order_date    DATE NOT NULL,
    status        VARCHAR(20) NOT NULL DEFAULT 'Pending'
                  CHECK(status IN ('Pending','Shipped','Delivered','Cancelled')),
    total_amount  DECIMAL(12,2) NOT NULL CHECK(total_amount >= 0),

    FOREIGN KEY (customer_id)
    REFERENCES customers(customer_id)
);

CREATE INDEX idx_orders_date
ON orders(order_date);

CREATE INDEX idx_orders_status
ON orders(status);

-- ============================================================
-- STEP 5: Create order_items Table
-- ============================================================

CREATE TABLE order_items (
    item_id       INT PRIMARY KEY,
    order_id      INT NOT NULL,
    product_id    INT NOT NULL,
    quantity      INT NOT NULL CHECK(quantity > 0),
    unit_price    DECIMAL(10,2) NOT NULL CHECK(unit_price > 0),
    discount_pct  DECIMAL(5,2) DEFAULT 0
                  CHECK(discount_pct BETWEEN 0 AND 100),

    FOREIGN KEY (order_id)
    REFERENCES orders(order_id),

    FOREIGN KEY (product_id)
    REFERENCES products(product_id)
);

-- ============================================================
-- STEP 6: Insert Customers
-- ============================================================

---INSERT INTO customers VALUES
---(101,'Aarav','Sharma','aarav.s@email.com','Mumbai','Maharashtra','2024-01-15',TRUE),
---(102,'Priya','Patel','priya.p@email.com','Ahmedabad','Gujarat','2024-02-20',FALSE),
---(103,'Rohan','Gupta','rohan.g@email.com','Delhi','Delhi','2024-03-10',TRUE),
---(104,'Sneha','Reddy','sneha.r@email.com','Hyderabad','Telangana','2024-04-05',FALSE),
---(105,'Vikram','Singh','vikram.s@email.com','Jaipur','Rajasthan','2024-05-12',TRUE),
---(106,'Ananya','Iyer','ananya.i@email.com','Chennai','Tamil Nadu','2024-06-18',FALSE),
---(107,'Karan','Mehta','karan.m@email.com','Pune','Maharashtra','2024-07-22',TRUE),
---(108,'Divya','Nair','divya.n@email.com','Kochi','Kerala','2024-08-30',FALSE);

-- ============================================================
-- STEP 7: Insert Products
-- ============================================================

-- INSERT INTO products VALUES
-- (201,'Wireless Earbuds','Electronics','BoAt',1499.00,250),
-- (202,'Cotton T-Shirt','Clothing','Levis',799.00,500),
-- (203,'Smart Watch','Electronics','Noise',2999.00,150),
-- (204,'Running Shoes','Clothing','Nike',4599.00,120),
-- (205,'Bluetooth Speaker','Electronics','JBL',3499.00,200),
-- (206,'Bedsheet Set','Home','Spaces',1299.00,300),
-- (207,'Laptop Stand','Electronics','AmazonBasics',899.00,180),
-- (208,'Cushion Covers (Set)','Home','HomeCenter',599.00,400);

-- ============================================================
-- STEP 8: Insert Orders
-- ============================================================

-- INSERT INTO orders VALUES
-- (1001,101,'2024-08-01','Delivered',4498.00),
-- (1002,102,'2024-08-03','Delivered',799.00),
-- (1003,103,'2024-08-05','Shipped',7498.00),
-- (1004,101,'2024-08-10','Delivered',3499.00),
-- (1005,104,'2024-08-12','Cancelled',2999.00),
-- (1006,105,'2024-08-15','Delivered',5898.00),
-- (1007,106,'2024-08-18','Pending',1299.00),
-- (1008,103,'2024-08-20','Delivered',899.00),
-- (1009,107,'2024-08-25','Shipped',6098.00),
-- (1010,108,'2024-08-28','Delivered',1598.00);

-- ============================================================
-- STEP 9: Insert Order Items
-- ============================================================

-- INSERT INTO order_items VALUES
-- (5001,1001,201,2,1499.00,0),
-- (5002,1001,207,1,899.00,10),
-- (5003,1002,202,1,799.00,0),
-- (5004,1003,203,1,2999.00,0),
-- (5005,1003,204,1,4599.00,5),
-- (5006,1004,205,1,3499.00,0),
-- (5007,1005,203,1,2999.00,0),
-- (5008,1006,201,1,1499.00,10),
-- (5009,1006,204,1,4599.00,5),
-- (5010,1007,206,1,1299.00,0),
-- (5011,1008,207,1,899.00,0),
-- (5012,1009,205,1,3499.00,0),
-- (5013,1009,208,2,599.00,15),
-- (5014,1010,206,1,1299.00,0),
-- (5015,1010,208,1,599.00,0);

-- ============================================================
-- STEP 10: Verify Data
-- ============================================================

SELECT * FROM customers;
SELECT * FROM products;
SELECT * FROM orders;
SELECT * FROM order_items;

-- ============================================================
-- SECTION A : SQL BASICS
-- ============================================================

-- ============================================================
-- Q1. Display all columns and rows from the customers table.
-- ============================================================

SELECT *
FROM customers;

-- ============================================================
-- Q2. Retrieve only the first_name, last_name and city of all customers.
-- ============================================================

SELECT first_name,
       last_name,
       city
FROM customers;

-- ============================================================
-- Q3. List all unique categories available in the products table.
-- ============================================================

SELECT DISTINCT category
FROM products;

-- ============================================================
-- Q4. Identify the Primary Key of each table.
-- Explain why a Primary Key must be UNIQUE and NOT NULL.
-- ============================================================

-- Primary Keys:
--
-- customers     -> customer_id
-- products      -> product_id
-- orders        -> order_id
-- order_items   -> item_id
--
-- A Primary Key uniquely identifies every record in a table.
-- It cannot contain duplicate values and cannot be NULL,
-- ensuring every row has a unique identifier.

-- ============================================================
-- Q5. What constraints are applied to the email column?
-- What happens if a duplicate email is inserted?
-- ============================================================

-- The email column has:
--
-- 1. UNIQUE Constraint
-- 2. NOT NULL Constraint
--
-- Duplicate email test:

INSERT INTO customers
VALUES
(
109,
'Test',
'User',
'aarav.s@email.com',
'Indore',
'Madhya Pradesh',
'2024-09-01',
FALSE
);

-- Expected Result:
--
-- ERROR 1062 (23000):
-- Duplicate entry 'aarav.s@email.com'
-- for key 'customers.email'
--
-- This happens because the UNIQUE constraint
-- prevents duplicate email addresses.

-- ============================================================
-- Q6. Try inserting a product with unit_price = -50.
-- Explain what happens.
-- ============================================================

INSERT INTO products
VALUES
(
209,
'Dummy Product',
'Electronics',
'DummyBrand',
-50.00,
100
);

-- Expected Result:
--
-- ERROR:
-- Check constraint 'products_chk_1' is violated
--
-- This happens because the CHECK constraint prevents inserting products with negative prices.

-- ============================================================
-- SECTION B : FILTERING & OPTIMIZATION (WHERE, Indexes)
-- ============================================================

-- ============================================================
-- Q7. Retrieve all orders with status = 'Delivered'.
-- ============================================================

SELECT *
FROM orders
WHERE status = 'Delivered';

-- ============================================================
-- Q8. Find all products in the 'Electronics' category
-- with a unit_price greater than ₹2000.
-- ============================================================

SELECT *
FROM products
WHERE category = 'Electronics'
  AND unit_price > 2000;

-- ============================================================
-- Q9. List all customers who joined in the year 2024
-- and belong to the state 'Maharashtra'.
-- ============================================================

SELECT *
FROM customers
WHERE join_date BETWEEN '2024-01-01' AND '2024-12-31'
  AND state = 'Maharashtra';

-- ============================================================
-- Q10. Find all orders placed between '2024-08-10'
-- and '2024-08-25' (inclusive) that are NOT cancelled.
-- ============================================================

SELECT *
FROM orders
WHERE order_date BETWEEN '2024-08-10' AND '2024-08-25'
  AND status <> 'Cancelled';

-- ============================================================
-- Q11. Explain what the index idx_orders_date does.
-- Write a sample query that benefits from this index.
-- ============================================================
--
-- The index 'idx_orders_date' is created on the order_date column.
-- It speeds up queries that search, filter, sort, or retrieve
-- records based on order_date by reducing the number of rows
-- the database engine must scan.
--
-- Without an index, MySQL performs a full table scan.
-- With the index, MySQL can directly locate the matching rows,
-- improving query performance, especially for large datasets.

-- Sample Query:

SELECT *
FROM orders
WHERE order_date BETWEEN '2024-08-10' AND '2024-08-25';

-- ============================================================
-- Q12. Will the following query use an index?
--
-- SELECT * FROM customers
-- WHERE YEAR(join_date) = 2024;
--
-- Explain why or why not.
-- Rewrite it to be index-friendly (SARGable).
-- ============================================================

-- Original Query

SELECT *
FROM customers
WHERE YEAR(join_date) = 2024;
--
-- No, the given query will not use an index on join_date.
--
-- Applying the YEAR() function to the join_date column
-- prevents MySQL from using an index efficiently because
-- the function must be evaluated for every row.
--
-- This results in a full table scan.

-- SARGable (Index-Friendly) Query:

SELECT *
FROM customers
WHERE join_date >= '2024-01-01'
  AND join_date < '2025-01-01';

-- This query compares the column directly without applying
-- any function, allowing MySQL to use an index on join_date
-- if one exists, resulting in faster query execution.

-- ============================================================
-- SECTION C : AGGREGATION (GROUP BY, SUM, COUNT, AVG, MIN, MAX)
-- ============================================================

-- ============================================================
-- Q13. Count the total number of orders in the orders table.
-- ============================================================

SELECT COUNT(*) AS total_orders
FROM orders;

-- ============================================================
-- Q14. Find the total revenue (SUM of total_amount)
-- from all 'Delivered' orders.
-- ============================================================

SELECT SUM(total_amount) AS total_revenue
FROM orders
WHERE status = 'Delivered';

-- ============================================================
-- Q15. Calculate the average unit_price of products
-- in each category.
-- ============================================================

SELECT category,
       AVG(unit_price) AS average_unit_price
FROM products
GROUP BY category;

-- ============================================================
-- Q16. For each order status, find the count of orders
-- and the total revenue.
-- Sort the result by total revenue in descending order.
-- ============================================================

SELECT status,
       COUNT(*) AS total_orders,
       SUM(total_amount) AS total_revenue
FROM orders
GROUP BY status
ORDER BY total_revenue DESC;

-- ============================================================
-- Q17. Find the most expensive (MAX) and cheapest (MIN)
-- product in each category.
-- ============================================================

SELECT category,
       MAX(unit_price) AS highest_price,
       MIN(unit_price) AS lowest_price
FROM products
GROUP BY category;

-- ============================================================
-- Q18. List all product categories where the average
-- unit_price is greater than ₹2000.
-- ============================================================

SELECT category,
       AVG(unit_price) AS average_unit_price
FROM products
GROUP BY category
HAVING AVG(unit_price) > 2000;

-- ============================================================
-- SECTION D : JOINS & RELATIONSHIPS
-- ============================================================

-- ============================================================
-- Q19. Write an INNER JOIN query to display each order along
-- with the customer's first_name and last_name.
-- Show: order_id, order_date, first_name, last_name,
-- total_amount.
-- ============================================================

SELECT o.order_id,
       o.order_date,
       c.first_name,
       c.last_name,
       o.total_amount
FROM orders o
INNER JOIN customers c
ON o.customer_id = c.customer_id;

-- ============================================================
-- Q20. Using a LEFT JOIN, list ALL customers and their orders
-- (if any). Customers with no orders should still appear with
-- NULL values for order columns.
-- ============================================================

SELECT c.customer_id,
       c.first_name,
       c.last_name,
       o.order_id,
       o.order_date,
       o.status,
       o.total_amount
FROM customers c
LEFT JOIN orders o
ON c.customer_id = o.customer_id
ORDER BY c.customer_id;

-- ============================================================
-- Q21. Write a query using JOINs across three tables
-- (orders → order_items → products) to show:
-- order_id, product_name, quantity,
-- unit_price, and discount_pct.
-- ============================================================

SELECT o.order_id,
       p.product_name,
       oi.quantity,
       oi.unit_price,
       oi.discount_pct
FROM orders o
INNER JOIN order_items oi
ON o.order_id = oi.order_id
INNER JOIN products p
ON oi.product_id = p.product_id
ORDER BY o.order_id;

-- ============================================================
-- Q22. Explain the difference between LEFT JOIN and RIGHT JOIN.
-- When would you use a FULL OUTER JOIN?
-- ============================================================

-- LEFT JOIN:
-- Returns all rows from the left table and the matching rows
-- from the right table. If no matching row exists, NULL values
-- are returned for the right table columns.

-- RIGHT JOIN:
-- Returns all rows from the right table and the matching rows
-- from the left table. If no matching row exists, NULL values
-- are returned for the left table columns.

-- FULL OUTER JOIN:
-- Returns all rows from both tables.
-- Matching rows are combined, while non-matching rows from
-- either table are returned with NULL values.
--
-- MySQL does not support FULL OUTER JOIN directly.
-- However, it can be simulated using a UNION of LEFT JOIN and RIGHT JOIN.

---------------------------------------------------------------

-- ============================================================
-- Q23. Identify all Foreign Key relationships in the schema.
-- Explain what happens if customer_id = 999 is inserted into
-- the orders table.
-- ============================================================

-- Foreign Key Relationships:
--
-- orders.customer_id
--     REFERENCES customers(customer_id)
--
-- order_items.order_id
--     REFERENCES orders(order_id)
--
-- order_items.product_id
--     REFERENCES products(product_id)

-- Example:

INSERT INTO orders
VALUES
(
1011,
999,
'2024-09-01',
'Pending',
1000.00
);

-- Expected Result:
--
-- ERROR 1452 (23000):
-- Cannot add or update a child row:
-- a foreign key constraint fails.
--
-- Explanation:
-- customer_id = 999 does not exist in the customers table.
-- The FOREIGN KEY constraint enforces referential integrity
-- and prevents insertion of invalid references.

---------------------------------------------------------------
-- ============================================================
-- SECTION E : ADVANCED CONCEPTS (CASE, ACID, Transactions)
-- ============================================================

-- ============================================================
-- Q24. Classify products into price tiers using CASE.
-- ============================================================

SELECT
    product_name,
    unit_price,
    CASE
        WHEN unit_price < 1000 THEN 'Budget'
        WHEN unit_price BETWEEN 1000 AND 3000 THEN 'Mid-Range'
        ELSE 'Premium'
    END AS price_tier
FROM products;

-- ============================================================
-- Q25. Count Delivered vs Not Delivered orders
-- using CASE inside aggregate functions.
-- ============================================================

SELECT
    SUM(CASE
            WHEN status = 'Delivered' THEN 1
            ELSE 0
        END) AS delivered_orders,

    SUM(CASE
            WHEN status <> 'Delivered' THEN 1
            ELSE 0
        END) AS not_delivered_orders
FROM orders;

-- ============================================================
-- Q26. Explain ACID Properties.
-- ============================================================

-- ACID stands for:
--
-- A - Atomicity
-- A transaction is treated as a single unit of work.
-- Either every operation succeeds or none of them are applied.
--
-- C - Consistency
-- A transaction always takes the database from one valid state
-- to another while maintaining all rules and constraints.
--
-- I - Isolation
-- Multiple transactions execute independently without
-- interfering with one another.
--
-- D - Durability
-- Once a transaction is committed, the changes become permanent,
-- even if the database server crashes immediately afterward.

-- ============================================================
-- Q27. SQL Transaction Example
-- ============================================================

START TRANSACTION;

-- Step 1: Insert a new order

INSERT INTO orders
(order_id, customer_id, order_date, status, total_amount)
VALUES
(1011, 102, CURDATE(), 'Pending', 1598.00);

-- Step 2: Insert two order items

INSERT INTO order_items
(item_id, order_id, product_id, quantity, unit_price, discount_pct)
VALUES
(5016, 1011, 206, 1, 1299.00, 0);

INSERT INTO order_items
(item_id, order_id, product_id, quantity, unit_price, discount_pct)
VALUES
(5017, 1011, 208, 1, 299.00, 0);

-- Step 3: Update stock quantities

UPDATE products
SET stock_qty = stock_qty - 1
WHERE product_id = 206;

UPDATE products
SET stock_qty = stock_qty - 1
WHERE product_id = 208;

-- Step 4:
-- If every statement executes successfully,
-- commit the transaction.

COMMIT;

-- If any statement fails before COMMIT,
-- execute the following instead:

-- ROLLBACK;
----------------Assignment 2 Finished---------------------------