# Databricks notebook source
# MAGIC %md
# MAGIC # 05 - Historical Revenue Recalculation & Delta Lake MERGE
# MAGIC 
# MAGIC ### Objective:
# MAGIC 1. **Selective Recalculation**: Join Silver transactions with `affected_dates` on `txn_date`.
# MAGIC 2. **Full Historical Recomputation**: Compute `SUM(amount)` across **ALL valid transactions** (both on-time and late) for those affected dates.
# MAGIC 3. **Surgical Delta MERGE**: Update the Gold Delta table matching on `target.txn_date = source.txn_date` without rewriting the entire table.

# COMMAND ----------
import sys, os
sys.path.append(os.path.abspath(".."))

from pyspark.sql import functions as F
from config.project_config import config
from src.late_transactions import LateTransactionDetector
from src.historical_correction import HistoricalRevenueCorrector

# COMMAND ----------
# MAGIC %md
# MAGIC ### Step 1: Detect Affected Historical Dates

# COMMAND ----------
silver_df = spark.read.format("delta").load(config.SILVER_PATH)
detector = LateTransactionDetector(config)
late_df = detector.detect_late_transactions(silver_df)
affected_dates_df = detector.get_affected_historical_dates(late_df)

print(f"Number of historical dates to correct: {affected_dates_df.count()}")

# COMMAND ----------
# MAGIC %md
# MAGIC ### Step 2: Capture Snapshot of Gold Table BEFORE Correction

# COMMAND ----------
gold_before_df = spark.read.format("delta").load(config.GOLD_PATH)

# COMMAND ----------
# MAGIC %md
# MAGIC ### Step 3: Recalculate Complete Daily Revenue for Affected Dates Only

# COMMAND ----------
corrector = HistoricalRevenueCorrector(config)
recomputed_revenue_df = corrector.recalculate_affected_revenue(silver_df, affected_dates_df)

print(f"Recalculated Records Ready for MERGE: {recomputed_revenue_df.count()}")
display(recomputed_revenue_df.limit(10))

# COMMAND ----------
# MAGIC %md
# MAGIC ### Step 4: Execute Delta Lake MERGE

# COMMAND ----------
merge_result = corrector.merge_into_gold(spark, recomputed_revenue_df)
print(f"Delta MERGE Execution Result: {merge_result}")

# COMMAND ----------
# MAGIC %md
# MAGIC ### Step 5: Read Gold Table AFTER Correction & Build Reconciliation Audit

# COMMAND ----------
gold_after_df = spark.read.format("delta").load(config.GOLD_PATH)
comparison_df = corrector.compute_before_after_comparison(
    gold_before_df, 
    gold_after_df, 
    affected_dates_df
)

print("=== Sample Corrected Historical Dates (Before vs After) ===")
display(comparison_df.limit(20))
