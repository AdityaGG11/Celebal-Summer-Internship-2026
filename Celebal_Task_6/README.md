# Week 6 – Spark Architecture and Data Processing using Apache Spark

## 📌 Overview

This project demonstrates the core concepts of Apache Spark Architecture and efficient data processing using **PySpark**. It covers Spark Architecture, Lazy Evaluation, DAG (Lineage Graph), DataFrame transformations, schema handling, filtering, null handling, CSV and Parquet file formats, and building an end-to-end Spark data processing pipeline.

This assignment was completed as part of the **Celebal Technologies Summer Internship 2026 – Week 6 Assignment**.

---

## 🎯 Objectives

- Understand Apache Spark Architecture
- Learn the roles of Driver, Cluster Manager, and Executors
- Understand Lazy Evaluation and DAG (Lineage Graph)
- Read data from CSV and Parquet files
- Perform DataFrame filtering and column selection
- Rename columns and cast data types
- Add new calculated columns
- Handle null values efficiently
- Understand Predicate Pushdown
- Compare CSV and Parquet file formats
- Build an end-to-end Spark data pipeline
- Save processed data in CSV and Parquet formats
- Follow Spark best practices for large datasets

---

## 🛠️ Technologies Used

- Apache Spark
- PySpark
- Python
- Google Colab

---

## 📂 Dataset

A sample e-commerce orders dataset was used to demonstrate Spark DataFrame operations.

### Dataset Columns

- user_id
- product_id
- category
- old_name
- price
- base_price
- amount
- status
- region
- priority

---

## ✅ Tasks Performed

- Read CSV file with schema inference
- Display dataset and inspect schema
- Filter and select required columns
- Rename DataFrame columns
- Cast data types
- Add calculated columns
- Filter records using multiple conditions
- Handle null values
- Write DataFrame to Parquet
- Read Parquet files
- Save processed data as CSV
- Build a complete Spark data pipeline
- Demonstrate Lazy Evaluation
- View Spark execution plan (DAG)
- Compare Transformations and Actions
- Demonstrate best practices using `show()` instead of `collect()`

---

## 📁 Project Structure

```text
Celebal_Task_6
│
├── README.md
├── Week_6_Report.pdf
├── Celebal_Week6_Spark_Architecture.ipynb
├── ecommerce_orders.csv
├── input_parquet/
└── output_csv/
```

---

## ▶️ How to Run

1. Open the notebook using Google Colab.
2. Install PySpark.
3. Upload the dataset (`ecommerce_orders.csv`).
4. Run all notebook cells sequentially.
5. The notebook will automatically:
   - Read the dataset
   - Perform Spark transformations
   - Generate Parquet output
   - Generate processed CSV output

---

## 📚 Concepts Covered

- Spark Architecture
- Driver
- Cluster Manager
- Executors
- Client Mode vs Cluster Mode
- Lazy Evaluation
- DAG (Lineage Graph)
- Transformations
- Actions
- Schema Inference
- DataFrame Operations
- Predicate Pushdown
- CSV vs Parquet
- Null Handling
- Data Processing Pipeline
- Spark Performance Best Practices

---

## 📈 Pipeline Overview

```text
Read CSV
      │
      ▼
Schema Inference
      │
      ▼
Transform DataFrame
      │
      ▼
Apply Filters
      │
      ▼
Handle Null Values
      │
      ▼
Write Parquet
      │
      ▼
Read Parquet
      │
      ▼
Write Processed CSV
```

---

## 📖 Learning Outcomes

By completing this assignment, the following Spark concepts were implemented and demonstrated:

- Reading structured datasets using Spark DataFrames
- Performing efficient DataFrame transformations
- Building optimized Spark execution pipelines
- Understanding Lazy Evaluation and execution plans
- Working with columnar storage formats such as Parquet
- Applying filtering and null handling techniques
- Writing processed datasets into multiple storage formats

---

## 👨‍💻 Author

**Aditya Kumar**

B.Tech Computer Science Engineering (Cloud Computing & Blockchain)

DIT University, Dehradun

---

## ⭐ Internship

Completed as part of the **Celebal Technologies Summer Internship 2026**.