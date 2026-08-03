# Week 7 - Delta Lake MERGE Operation using PySpark

## 📌 Overview

This project demonstrates the implementation of Delta Lake MERGE operations using PySpark. The assignment focuses on handling incremental data by updating existing records and inserting new records into a Delta Table.

---

## 🎯 Objectives

- Configure Apache Spark with Delta Lake
- Load CSV data into a Spark DataFrame
- Perform data cleaning
- Create a Delta Table
- Generate an incremental dataset
- Perform MERGE operation
- Validate updated and inserted records

---

## 🛠️ Technologies Used

- Python
- Apache Spark (PySpark)
- Delta Lake
- Google Colab

---

## 📂 Project Structure

```
Assignment_7/
│
├── Sample - Superstore.csv
├── Celebal_Week7_DeltaLake_Merge.ipynb
├── Week_7_Report.pdf
└── README.md
```

---

## 📊 Dataset

- Dataset: Sample Superstore
- Total Records: 9994
- Total Columns: 21

---

## ⚙️ Steps Performed

1. Installed PySpark and Delta Lake
2. Created Spark Session with Delta Support
3. Loaded CSV Dataset
4. Performed Data Cleaning
5. Renamed columns for Delta compatibility
6. Created Delta Table
7. Created Incremental Dataset
8. Executed MERGE Operation
9. Validated updated and inserted records

---

## ✅ MERGE Logic

- Existing records were updated using **WHEN MATCHED UPDATE**
- New records were inserted using **WHEN NOT MATCHED INSERT**

Merge Key:

```
Row_ID
```

---

## 📈 Result

- Delta Table created successfully.
- Existing records updated.
- New records inserted.
- Final Delta Table validated successfully.

---

## 📚 Learning Outcomes

- Spark DataFrame operations
- Delta Lake architecture
- ACID transactions
- MERGE operation
- Incremental data processing
- Data validation using PySpark