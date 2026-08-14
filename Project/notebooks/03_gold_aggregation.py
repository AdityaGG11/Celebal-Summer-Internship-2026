# Databricks notebook source
# MAGIC %md
# MAGIC # 03 - Gold Layer: Initial Daily Revenue Aggregation Snapshot
# MAGIC 
# MAGIC ### Objective:
# MAGIC Compute the **Initial Gold Reporting Snapshot** from valid on-time Silver transactions available at initial reporting time (`ingestion_date == txn_date`).
# MAGIC 
# MAGIC ### Semantic Distinction:
# MAGIC - **Initial Gold Snapshot**: $283,398.81 across 585 on-time transactions. Represents the initial daily revenue before late-arriving transactions are discovered.
# MAGIC - **Late Transactions**: Arrive post-reporting (`ingestion_date > txn_date`) and are detected in Notebook 04.
# MAGIC - **Corrected Gold**: Surgically updated in Notebook 05 to include **ALL** valid transactions ($967,793.88).

# COMMAND ----------
import sys, os
sys.path.append(os.path.abspath(".."))

from pyspark.sql import functions as F
from config.project_config import config
from src.gold import GoldAggregation

# COMMAND ----------
# MAGIC %md
# MAGIC ### Step 1: Read Valid Silver Data

# COMMAND ----------
silver_df = spark.read.format("delta").load(config.SILVER_PATH)
total_silver_records = silver_df.count()
ontime_records = silver_df.filter(F.col("ingestion_date") == F.col("txn_date")).count()

print(f"Total Silver records:   {total_silver_records}")
print(f"On-time Silver records: {ontime_records}")

# COMMAND ----------
# MAGIC %md
# MAGIC ### Step 2: Compute Initial Gold Daily Revenue Snapshot (On-Time Only)

# COMMAND ----------
gold_agg = GoldAggregation(config)
initial_gold_df = gold_agg.process_initial_gold(spark, silver_df, ontime_only=True)

initial_gold_dates = initial_gold_df.count()
initial_gold_rev = initial_gold_df.select(F.sum("daily_revenue")).first()[0]

print(f"Initial Gold distinct transaction dates: {initial_gold_dates}")
print(f"Initial Gold total revenue:              ${initial_gold_rev:,.2f}")

# COMMAND ----------
# MAGIC %md
# MAGIC ### Step 3: Inspect Initial Gold Revenue Table

# COMMAND ----------
display(initial_gold_df.orderBy("txn_date").limit(20))
