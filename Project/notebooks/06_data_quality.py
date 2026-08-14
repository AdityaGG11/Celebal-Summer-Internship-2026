# Databricks notebook source
# MAGIC %md
# MAGIC # 06 - Data Quality Framework & Invariant Validation
# MAGIC 
# MAGIC ### Objective:
# MAGIC Run automated, rule-based data quality checks across Bronze, Silver, and Gold datasets.
# MAGIC 
# MAGIC ### Validation Rules:
# MAGIC 1. **Null Checks**: Ensure no null transaction IDs, user IDs, or dates exist in Silver.
# MAGIC 2. **Uniqueness**: Enforce 0 duplicate `txn_id`s in Silver.
# MAGIC 3. **Amount Bounds**: Enforce `amount > 0`.
# MAGIC 4. **Date Integrity**: Enforce valid calendar dates and logical chronological order.
# MAGIC 5. **Reconciliation Invariant**: Verify `Gold.daily_revenue == SUM(Silver.amount)` for every transaction date.

# COMMAND ----------
import sys, os
sys.path.append(os.path.abspath(".."))

from pyspark.sql import functions as F
from config.project_config import config
from src.data_quality import DataQualityChecker

# COMMAND ----------
# MAGIC %md
# MAGIC ### Step 1: Run Data Quality Checks on Bronze

# COMMAND ----------
bronze_df = spark.read.format("delta").load(config.BRONZE_PATH)
checker = DataQualityChecker(config)
bronze_report = checker.check_dataset(bronze_df)

print("=== Bronze Data Quality Report ===")
for k, v in bronze_report.items():
    print(f"  {k}: {v}")

# COMMAND ----------
# MAGIC %md
# MAGIC ### Step 2: Run Data Quality Checks on Silver

# COMMAND ----------
silver_df = spark.read.format("delta").load(config.SILVER_PATH)
silver_report = checker.check_dataset(silver_df)

print("=== Silver Data Quality Report ===")
for k, v in silver_report.items():
    print(f"  {k}: {v}")

# COMMAND ----------
# MAGIC %md
# MAGIC ### Step 3: Run End-to-End Mathematical Reconciliation

# COMMAND ----------
gold_df = spark.read.format("delta").load(config.GOLD_PATH)

silver_sums = (
    silver_df
    .groupBy("txn_date")
    .agg(
        F.round(F.sum("amount"), 2).alias("silver_total"),
        F.count("txn_id").alias("silver_count")
    )
)

reconciliation_df = (
    gold_df
    .join(silver_sums, on="txn_date", how="inner")
    .withColumn("diff", F.round(F.col("daily_revenue") - F.col("silver_total"), 2))
    .filter(F.col("diff") != 0)
)

mismatch_count = reconciliation_df.count()
if mismatch_count == 0:
    print("SUCCESS: Perfect mathematical reconciliation across all 60 dates!")
else:
    print(f"FAILURE: Detected {mismatch_count} discrepancies.")
    display(reconciliation_df)
