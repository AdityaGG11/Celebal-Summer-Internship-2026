# Databricks notebook source
# MAGIC %md
# MAGIC # 07 - Watermark & Incremental Control Table
# MAGIC 
# MAGIC ### Objective:
# MAGIC Maintain a Delta Lake control table (`watermark_control`) that records the high-watermark for pipeline stages.
# MAGIC 
# MAGIC ### Core Principle:
# MAGIC The watermark is ONLY updated AFTER all transformations, quality validations, and Delta MERGE commits succeed.

# COMMAND ----------
import sys, os
sys.path.append(os.path.abspath(".."))

from datetime import date
from pyspark.sql import functions as F
from config.project_config import config
from src.watermark import WatermarkManager

# COMMAND ----------
# MAGIC %md
# MAGIC ### Step 1: Initialize Watermark Control Table

# COMMAND ----------
watermark_mgr = WatermarkManager(config)
watermark_mgr.initialize_control_table(spark)

# COMMAND ----------
# MAGIC %md
# MAGIC ### Step 2: Query Existing Watermark

# COMMAND ----------
current_watermark = watermark_mgr.get_watermark(spark, "gold_daily_revenue")
print(f"Current High-Watermark for 'gold_daily_revenue': {current_watermark}")

# COMMAND ----------
# MAGIC %md
# MAGIC ### Step 3: Advance Watermark After Successful Batch Processing

# COMMAND ----------
# Read max transaction date from Silver as high watermark
silver_df = spark.read.format("delta").load(config.SILVER_PATH)
max_txn_date = silver_df.select(F.max("txn_date")).first()[0]
total_records = silver_df.count()

print(f"Advancing watermark to: {max_txn_date} with {total_records} records processed.")
watermark_mgr.update_watermark(spark, "gold_daily_revenue", max_txn_date, total_records)

# COMMAND ----------
# MAGIC %md
# MAGIC ### Step 4: Display Watermark Control Table

# COMMAND ----------
control_df = spark.read.format("delta").load(config.WATERMARK_PATH)
display(control_df)
