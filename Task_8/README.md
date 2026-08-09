# Week 8 - E-Commerce Order Analytics System

## 📌 Overview

This project implements an E-Commerce Order Analytics System using Python and SQL.

The project generates synthetic e-commerce data with intentional data-quality issues, cleans and validates the data, loads it into a SQLite database, performs analytical SQL queries, and provides a command-line reporting tool.

---

## 🎯 Objectives

- Generate synthetic e-commerce datasets
- Introduce realistic data-quality issues
- Clean and validate the generated data
- Check referential integrity
- Load cleaned data into SQLite
- Perform basic, intermediate, and advanced SQL analysis
- Build a command-line reporting tool
- Handle required edge cases
- Analyze frequently bought-together products

---

## 🛠️ Technologies Used

- Python
- Pandas
- SQLite
- SQL
- Python `unittest`

---

## 📂 Project Structure

```text
Task_8/
│
├── data/
│   ├── raw/
│   │   ├── customers.csv
│   │   ├── orders.csv
│   │   ├── order_items.csv
│   │   └── products.csv
│   │
│   └── cleaned/
│       ├── customers_cleaned.csv
│       ├── orders_cleaned.csv
│       ├── order_items_cleaned.csv
│       ├── products_cleaned.csv
│       ├── orphan_order_items.csv
│       └── data_quality_report.md
│
├── database/
│   └── ecommerce.db
│
├── sql/
│   ├── 01_revenue_per_category.sql
│   ├── 02_top_10_customers.sql
│   ├── 03_last_12_months.sql
│   ├── 04_undelivered_customers.sql
│   ├── 05_excessive_returns.sql
│   ├── 06_category_return_rate.sql
│   ├── 07_running_totals.sql
│   ├── 08_dense_rank.sql
│   ├── 09_lag_lead.sql
│   ├── 10_multi_level_cte.sql
│   ├── 11_ntile_segmentation.sql
│   ├── 12_yoy_comparison.sql
│   ├── 13_first_last_value.sql
│   ├── 14_cumulative_distribution.sql
│   ├── 15_cohort_analysis.sql
│   ├── 16_self_join_window.sql
│   └── 17_frequently_bought_together.sql
│
├── src/
│   ├── data_generation/
│   │   └── generate_data.py
│   ├── data_cleaning/
│   │   └── clean_data.py
│   ├── database/
│   │   └── load_database.py
│   ├── analytics/
│   │   └── run_queries.py
│   └── cli/
│       └── report.py
│
├── tests/
│   └── test_task8.py
│
├── requirements.txt
└── README.md