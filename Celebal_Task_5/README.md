# Week 5 - Spark Data Cleaning, Transformation and Aggregation using DataFrames

## 📌 Overview

This project demonstrates the fundamentals of Apache Spark using PySpark DataFrames. The assignment focuses on understanding Spark concepts and implementing common data processing operations such as data cleaning, filtering, transformations, aggregations, schema modification, and building a complete data processing pipeline.

This work was completed as part of the **Celebal Technologies Summer Internship 2026 – Week 5 Assignment**.

---

# 🎯 Objectives

The objectives of this assignment are to:

- Understand the limitations of traditional MapReduce.
- Learn the advantages of Apache Spark and in-memory computing.
- Understand Spark DataFrame concepts and immutability.
- Perform data cleaning operations.
- Remove duplicate records.
- Handle null and missing values.
- Apply filtering conditions on datasets.
- Perform aggregation using Spark functions.
- Group data using `groupBy()`.
- Understand wide transformations and shuffle operations.
- Modify DataFrame schemas.
- Build a complete Spark data processing pipeline.

---

# 🛠 Technologies Used

- Apache Spark
- PySpark
- Python 3
- Google Colab
- CSV Dataset

---

# 📂 Dataset

**Dataset:** Ecommerce Sales Dataset

The dataset contains sample e-commerce sales information including:

- Order Date
- Order ID
- Customer ID
- Product ID
- Product Category
- Product Name
- Quantity Sold
- Unit Price
- Discount
- Payment Method
- Customer Location
- Order Status
- Shipping Cost
- Profit Margin
- Customer Age
- Customer Gender
- Customer Segment
- Review Rating
- Total Sales
- Discounted Price

---

# 📋 Assignment Tasks

The notebook covers all Week 5 assignment questions, including:

## ✅ Spark Fundamentals

- MapReduce limitations
- Spark In-Memory Computing
- DataFrame immutability
- Shuffle operations
- Wide transformations

## ✅ Data Cleaning

- Removing duplicate records
- Handling null values
- Filling missing values
- Removing invalid records

## ✅ Data Filtering

- Applying multiple filter conditions
- Filtering by category, location, and age
- Conditional filtering

## ✅ Aggregation

- Count
- Sum
- Average
- Minimum
- Maximum
- Multiple aggregations using `.agg()`

## ✅ GroupBy Operations

- Aggregating grouped records
- Applying conditions on grouped results

## ✅ Schema Modification

- Renaming columns
- Type casting
- Timestamp conversion
- Schema verification

## ✅ Final Processing Pipeline

- Duplicate removal
- Null value handling
- Data aggregation
- Revenue calculation

---

# 📚 Learning Outcomes

After completing this assignment, I gained practical experience with:

- Apache Spark architecture
- Spark DataFrames
- Data cleaning techniques
- Data transformations
- Filtering large datasets
- Aggregation operations
- GroupBy processing
- Schema management
- Spark execution concepts
- Building ETL-style data pipelines using PySpark

---

# 📁 Project Structure

```
Celebal_Task_5/
│
├── Celebal_Week5_Spark_DataFrame.ipynb
├── ecommerce_sales_data.csv
├── Week_5_Report.pdf
└── README.md
```

---

# ▶️ How to Run

1. Open **Google Colab** or a local Jupyter Notebook.
2. Install PySpark (if not already installed).

```python
!pip install pyspark
```

3. Upload the dataset (`ecommerce_sales_data.csv`).
4. Open the notebook `Celebal_Week5_Spark_DataFrame.ipynb`.
5. Run all cells sequentially to reproduce the results.

---

# 📊 Outputs

The notebook demonstrates:

- Spark Session creation
- Dataset loading
- Schema inspection
- Duplicate removal
- Null value handling
- Data filtering
- Aggregation operations
- GroupBy transformations
- Schema modification
- Timestamp conversion
- Complete data processing pipeline

---

# 💡 Key Concepts Demonstrated

- Spark DataFrames
- Lazy Evaluation
- Transformations vs Actions
- DataFrame Immutability
- In-Memory Processing
- Shuffle Operations
- Wide Transformations
- Data Cleaning
- Aggregation Functions
- ETL Pipeline Development

---

## 👨‍💻 Author

**Aditya Kumar**

**Celebal Technologies Summer Internship 2026**

**Week 3 – DataFrames Assignment**