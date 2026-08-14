# Databricks notebook source
# MAGIC %md
# MAGIC # 04 - Late Transaction Detection & Affected Historical Dates
# MAGIC 
# MAGIC ### Objective:
# MAGIC 1. Detect all transactions where `ingestion_date > txn_date`.
# MAGIC 2. Quantify arrival lag distribution (`arrival_lag_days`).
# MAGIC 3. Identify the distinct set of **affected historical dates** that require surgical recalculation.
# MAGIC 
# MAGIC ### Core Principle:
# MAGIC We do NOT blindly recompute every single date in the historical database. We extract ONLY the dates impacted by late transactions.

# COMMAND ----------
import sys, os
sys.path.append(os.path.abspath(".."))

from pyspark.sql import functions as F
from config.project_config import config
from src.late_transactions import LateTransactionDetector

# COMMAND ----------
# MAGIC %md
# MAGIC ### Step 1: Read Curated Silver Transactions

# COMMAND ----------
silver_df = spark.read.format("delta").load(config.SILVER_PATH)
detector = LateTransactionDetector(config)

# COMMAND ----------
# MAGIC %md
# MAGIC ### Step 2: Separate On-Time vs Late Transactions

# COMMAND ----------
late_df = detector.detect_late_transactions(silver_df)
ontime_df = detector.detect_ontime_transactions(silver_df)

metrics = detector.get_metrics(silver_df)

print("=== Transaction Arrival Breakdown ===")
for k, v in metrics.items():
    print(f"  {k}: {v}")

# COMMAND ----------
# MAGIC %md
# MAGIC ### Step 3: Extract Affected Historical Dates

# COMMAND ----------
affected_dates_df = detector.get_affected_historical_dates(late_df)
print(f"Total Unique Historical Dates Affected: {affected_dates_df.count()}")

# COMMAND ----------
# MAGIC %md
# MAGIC ### Step 4: Display Sample Late Transactions with Arrival Lag

# COMMAND ----------
display(late_df.orderBy(F.col("arrival_lag_days").desc()).limit(15))

# COMMAND ----------
# MAGIC %md
# MAGIC ### Step 5: Display Affected Historical Dates

# COMMAND ----------
display(affected_dates_df)
