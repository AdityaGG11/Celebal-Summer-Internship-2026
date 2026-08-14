# Databricks notebook source
# MAGIC %md
# MAGIC # 02 - Silver Layer: Cleaning, Validation, Type Casting & Deduplication
# MAGIC 
# MAGIC ### Objective:
# MAGIC Transform raw Bronze data into a clean, curated, and strictly typed **Silver Delta table**.
# MAGIC 
# MAGIC ### Transformations:
# MAGIC 1. **Explicit Type Casting**: Cast strings to `BIGINT`, `DATE`, and `DECIMAL(18,2)`.
# MAGIC 2. **Data Quality Validation**: Filter out null `txn_id`, null dates, negative or zero amounts.
# MAGIC 3. **Quarantine Routing**: Route invalid transactions to `silver_quarantine` Delta table with error reasons.
# MAGIC 4. **Deterministic Deduplication**: Enforce exactly one record per `txn_id` using windowing ordered by `ingestion_date DESC`.

# COMMAND ----------
import sys, os
sys.path.append(os.path.abspath(".."))

from pyspark.sql import functions as F
from config.project_config import config
from src.silver import SilverTransformation
from src.data_quality import DataQualityChecker

# COMMAND ----------
# MAGIC %md
# MAGIC ### Step 1: Read Bronze Delta Table

# COMMAND ----------
bronze_df = spark.read.format("delta").load(config.BRONZE_PATH)
print(f"Bronze source count: {bronze_df.count()}")

# COMMAND ----------
# MAGIC %md
# MAGIC ### Step 2: Clean, Type-Cast, Validate & Deduplicate

# COMMAND ----------
silver_transformer = SilverTransformation(config)
clean_silver_df, quarantine_df = silver_transformer.process(spark, bronze_df)

valid_count = clean_silver_df.count()
quarantine_count = quarantine_df.count()

print(f"Valid Silver Records:       {valid_count}")
print(f"Quarantined Records:       {quarantine_count}")

# COMMAND ----------
# MAGIC %md
# MAGIC ### Step 3: Run Data Quality Audit on Silver

# COMMAND ----------
dq_checker = DataQualityChecker(config)
silver_dq_report = dq_checker.check_dataset(clean_silver_df)

print("=== Silver Data Quality Audit Report ===")
for check, val in silver_dq_report.items():
    print(f"  {check}: {val}")

# COMMAND ----------
# MAGIC %md
# MAGIC ### Step 4: Display Clean Silver Records

# COMMAND ----------
display(clean_silver_df.orderBy("txn_date", "txn_id").limit(15))
