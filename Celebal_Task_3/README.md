# Celebal Technologies Summer Internship 2026
## Week 3 – Advanced SQL using Subqueries, CTEs & Window Functions

## 📌 Objective

The objective of this assignment is to perform SQL-based sales data analysis on the Superstore dataset using advanced SQL concepts. The task focuses on applying Subqueries, Common Table Expressions (CTEs), Window Functions, JOINs, and Aggregate Functions to solve business-oriented analytical problems.

---

## 🛠️ Tools & Technologies

- MySQL Server 8.0
- MySQL Workbench 8.0 CE
- SQL
- Superstore Dataset (CSV)
- Git & GitHub

---

## 📂 Dataset

The assignment uses the **Superstore Dataset**, which contains transactional sales records of a retail business.

The dataset includes information such as:

- Order Details
- Customer Information
- Product Information
- Sales
- Quantity
- Discount
- Profit
- Category & Sub-Category
- Region
- Segment
- Shipping Details

---

## 📁 Database Design

The dataset was first imported into a raw table:

- `superstore_raw`

The data was then normalized into the following relational tables:

- `customers`
- `orders`
- `products`

Data was transferred from the raw table into the normalized tables using `INSERT INTO ... SELECT ... GROUP BY` queries.

---

## 📚 SQL Concepts Implemented

### 1. Subqueries

Implemented nested queries to solve analytical problems such as:

- Finding orders with sales greater than the average sales
- Finding the highest sales order for each customer

---

### 2. Common Table Expressions (CTEs)

Used CTEs to simplify complex analytical queries, including:

- Calculating total sales for each customer
- Identifying customers with above-average total sales

---

### 3. Window Functions

Applied Window Functions for advanced reporting:

- `RANK()`
- `ROW_NUMBER()`
- `PARTITION BY`

These functions were used to rank customers and assign row numbers within customer groups.

---

### 4. JOIN Operations

Used JOINs to combine normalized tables and generate meaningful business reports.

---

## 📌 Assignment Queries

The following SQL queries were implemented:

- Find orders where sales are greater than the average sales.
- Find the highest sales order for each customer.
- Calculate total sales for each customer using CTE.
- Find customers whose total sales are above average.
- Rank customers based on total sales.
- Assign row numbers to each order within a customer.
- Display the top-ranked customers using Window Functions.
- Combine JOIN, CTE, and Window Functions to generate customer sales rankings.

---

## 📊 Business Analysis

The following business insights were generated from the dataset:

- Top 5 Customers by Total Sales
- Bottom 5 Customers by Total Sales
- Customers Who Placed Only One Order
- Customers with Above Average Total Sales
- Highest Order Value for Each Customer

---

## 📂 Repository Structure

```
Celebal_Task_3/
│
├── Dataset/
│   └── Superstore.csv
│
├── SQL/
│   ├── Assignment_3.sql
│
├── Screenshots/
│
├── Report/
│   └── Week_3_Task_Report.docx
│
└── README.md
```

---

## 📈 Key Insights

- Identified customers with the highest overall sales contribution.
- Compared customer sales against the overall average using Subqueries.
- Calculated cumulative customer sales using CTEs.
- Ranked customers using Window Functions for business reporting.
- Used JOIN operations to combine normalized data into meaningful reports.
- Demonstrated practical SQL techniques commonly used in business intelligence and sales analytics.

---

## 🎯 Learning Outcomes

Through this assignment, I gained practical experience in:

- Importing CSV data into MySQL
- Database normalization
- Creating relational database tables
- Using Aggregate Functions
- Writing SQL Subqueries
- Implementing Common Table Expressions (CTEs)
- Applying Window Functions (`RANK()`, `ROW_NUMBER()`)
- Using JOIN operations
- Solving real-world business queries
- Performing sales data analysis using SQL
- Writing structured and maintainable SQL scripts

---

## 🚀 Conclusion

This assignment provided hands-on experience in applying advanced SQL concepts to analyze a real-world sales dataset. By combining Subqueries, CTEs, Window Functions, Aggregate Functions, and JOIN operations, meaningful business insights were generated while following good database design practices through data normalization.

The project strengthened my understanding of SQL-based analytical querying and demonstrated how relational databases can be used for reporting and decision-making.

---

## 👨‍💻 Author

**Aditya Kumar**

**Celebal Technologies Summer Internship 2026**

**Week 3 – Advanced SQL Assignment**