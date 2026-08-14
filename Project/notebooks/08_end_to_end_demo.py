# Databricks notebook source
# MAGIC %md
# MAGIC # 08 - Master End-to-End Demonstration: Late Transaction Handling & Historical Revenue Correction
# MAGIC 
# MAGIC ### Project Architecture:
# MAGIC ```text
# MAGIC Raw CSV Files (Databricks Auto Loader) ──► Bronze Delta ──► Silver Delta (Clean/Dedup/Quarantine)
# MAGIC                                                                     │
# MAGIC                                                                     ▼
# MAGIC                                                             Initial Gold Delta
# MAGIC                                                          ($283,398.81 on-time snapshot)
# MAGIC                                                                     │
# MAGIC                              ┌──────────────────────────────────────┴──────────────────────────────────────┐
# MAGIC                              ▼                                                                            ▼
# MAGIC                   Late Transaction Detection                                                    Unaffected Dates
# MAGIC                    (ingestion_date > txn_date)                                                  (Isolated & Untouched)
# MAGIC                              │
# MAGIC                              ▼
# MAGIC                   Affected Historical Dates
# MAGIC                    (DISTINCT txn_date)
# MAGIC                              │
# MAGIC                              ▼
# MAGIC                   Selective Recalculation
# MAGIC                   (ALL valid txns: on-time + late for affected dates)
# MAGIC                              │
# MAGIC                              ▼
# MAGIC                      Delta Lake MERGE
# MAGIC                   (target.txn_date = source.txn_date)
# MAGIC                              │
# MAGIC                              ▼
# MAGIC                     Corrected Gold Delta Table
# MAGIC                   ($967,793.88 complete historical revenue)
# MAGIC                              │
# MAGIC                              ▼
# MAGIC                     Watermark Updated Post-Commit
# MAGIC ```

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 1 — Dataset Overview
# MAGIC Inspect source dataset volume, date boundaries, and transaction ranges.

# COMMAND ----------
import sys, os
sys.path.append(os.path.abspath(".."))

from pyspark.sql import functions as F
from pyspark.sql import types as T
from delta.tables import DeltaTable
from config.project_config import config
from src.bronze import BronzeIngestion
from src.silver import SilverTransformation
from src.gold import GoldAggregation
from src.late_transactions import LateTransactionDetector
from src.historical_correction import HistoricalRevenueCorrector
from src.data_quality import DataQualityChecker
from src.watermark import WatermarkManager
from src.audit import DeltaAuditManager

# Load raw CSV directly for initial inspection
raw_csv_df = spark.read.option("header", "true").csv(f"{config.SOURCE_PATH}/*.csv")
total_raw_rows = raw_csv_df.count()

print(f"=== STEP 1: RAW DATASET METRICS ===")
print(f"Total Raw Transactions: {total_raw_rows}")

date_summary = raw_csv_df.select(
    F.min("txn_date").alias("min_txn_date"),
    F.max("txn_date").alias("max_txn_date"),
    F.min("ingestion_date").alias("min_ingestion_date"),
    F.max("ingestion_date").alias("max_ingestion_date"),
    F.countDistinct("user_id").alias("unique_users"),
    F.countDistinct("txn_date").alias("unique_txn_dates")
).collect()[0]

print(f"Transaction Date Range: {date_summary['min_txn_date']} to {date_summary['max_txn_date']}")
print(f"Ingestion Date Range:   {date_summary['min_ingestion_date']} to {date_summary['max_ingestion_date']}")
print(f"Unique Users:           {date_summary['unique_users']}")
print(f"Unique Dates:           {date_summary['unique_txn_dates']}")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 2 — Bronze Ingestion via Databricks Auto Loader (`cloudFiles`)
# MAGIC Ingest raw files via Auto Loader streaming into Bronze Delta table preserving raw schema and appending lineage metadata.
# MAGIC *Note: In Databricks execution, Auto Loader structured streaming with `trigger(availableNow=True)` is used. Batch mode is available as a local testing fallback.*

# COMMAND ----------
print("=== STEP 2: BRONZE INGESTION (AUTO LOADER) ===")
bronze_ingestion = BronzeIngestion(config)

# Databricks Auto Loader Execution Path
print("Starting Auto Loader streaming ingestion with cloudFiles...")
stream_df = bronze_ingestion.read_autoloader_stream(spark)
streaming_query = bronze_ingestion.write_autoloader_stream(stream_df, trigger_available_now=True)
streaming_query.awaitTermination()

# Load Bronze Delta table for downstream processing
bronze_df = spark.read.format("delta").load(config.BRONZE_PATH)
bronze_count = bronze_df.count()

print(f"Bronze Delta Records Ingested via Auto Loader: {bronze_count}")
display(bronze_df.select("txn_id", "user_id", "txn_date", "amount", "ingestion_date", "_source_file").limit(5))

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 3 — Silver Transformation & Data Quality
# MAGIC Clean, type-cast, quarantine invalid records, and deterministically deduplicate transactions.

# COMMAND ----------
print("=== STEP 3: SILVER TRANSFORMATION & QUALITY ===")
silver_transformer = SilverTransformation(config)
clean_silver_df, quarantine_df = silver_transformer.process(spark, bronze_df)

valid_silver_count = clean_silver_df.count()
quarantine_count = quarantine_df.count()

print(f"Valid Silver Records:       {valid_silver_count}")
print(f"Quarantined Records:       {quarantine_count}")

# Run data quality validation
dq_checker = DataQualityChecker(config)
dq_report = dq_checker.check_dataset(clean_silver_df)
print("Data Quality Verification Passed:", dq_report["is_clean"])
display(clean_silver_df.limit(5))

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 4 — Initial Gold Daily Revenue Snapshot
# MAGIC Calculate initial baseline daily revenue using transactions available at initial reporting time (`ingestion_date == txn_date`).

# COMMAND ----------
print("=== STEP 4: INITIAL GOLD AGGREGATION SNAPSHOT ===")
gold_agg = GoldAggregation(config)
# Compute initial baseline from on-time transactions only
initial_gold_df = gold_agg.process_initial_gold(spark, clean_silver_df, ontime_only=True)

initial_gold_count = initial_gold_df.count()
initial_gold_rev = initial_gold_df.select(F.sum("daily_revenue")).first()[0]

print(f"Initial Gold Snapshot: {initial_gold_count} dates | Initial Revenue: ${initial_gold_rev:,.2f}")
display(initial_gold_df.orderBy("txn_date").limit(5))

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 5 — Late Transaction Detection
# MAGIC Identify transactions arriving after their business transaction date (`ingestion_date > txn_date`).

# COMMAND ----------
print("=== STEP 5: LATE TRANSACTION DETECTION ===")
detector = LateTransactionDetector(config)
late_df = detector.detect_late_transactions(clean_silver_df)
metrics = detector.get_metrics(clean_silver_df)

print(f"Total Transactions:   {metrics['total_transactions']}")
print(f"On-Time Transactions: {metrics['ontime_transactions']}")
print(f"Late Transactions:    {metrics['late_transactions']} ({metrics['late_ratio_pct']}%)")
print(f"Affected Dates Count: {metrics['affected_dates_count']}")

display(late_df.orderBy(F.col("arrival_lag_days").desc()).limit(5))

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 6 — Identify Affected Historical Dates
# MAGIC Extract distinct `txn_date` values requiring selective recalculation.

# COMMAND ----------
print("=== STEP 6: AFFECTED HISTORICAL DATES ===")
affected_dates_df = detector.get_affected_historical_dates(late_df)
total_dates_count = clean_silver_df.select("txn_date").distinct().count()
affected_count = affected_dates_df.count()
unaffected_count = total_dates_count - affected_count

print(f"Total Historical Dates:        {total_dates_count}")
print(f"Affected Dates to Recalculate: {affected_count}")
print(f"Unaffected Dates (Skipped):    {unaffected_count}")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 7 — Selective Revenue Recalculation
# MAGIC Recalculate full revenue using **ALL valid transactions** (on-time + late) for affected dates only.

# COMMAND ----------
print("=== STEP 7: SELECTIVE REVENUE RECALCULATION ===")
corrector = HistoricalRevenueCorrector(config)
recomputed_revenue_df = corrector.recalculate_affected_revenue(clean_silver_df, affected_dates_df)

print(f"Recalculated Records Generated: {recomputed_revenue_df.count()}")
display(recomputed_revenue_df.limit(5))

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 8 — Delta Lake MERGE
# MAGIC Execute surgical MERGE into Gold Delta table.

# COMMAND ----------
print("=== STEP 8: DELTA LAKE MERGE ===")
merge_result = corrector.merge_into_gold(spark, recomputed_revenue_df)
print("Delta MERGE status:", merge_result)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 9 — Final Corrected Gold Table
# MAGIC Display the updated Gold daily revenue records.

# COMMAND ----------
print("=== STEP 9: FINAL CORRECTED GOLD TABLE ===")
final_gold_df = spark.read.format("delta").load(config.GOLD_PATH)
final_gold_count = final_gold_df.count()
final_gold_rev = final_gold_df.select(F.sum("daily_revenue")).first()[0]

print(f"Final Gold Record Count: {final_gold_count}")
print(f"Final Corrected Revenue: ${final_gold_rev:,.2f}")
display(final_gold_df.orderBy("txn_date").limit(10))

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 10 — Mathematical Invariant Validation
# MAGIC Prove that `Gold.daily_revenue == SUM(all valid Silver transactions)` for all dates.

# COMMAND ----------
print("=== STEP 10: INVARIANT VALIDATION ===")
silver_expected = (
    clean_silver_df
    .groupBy("txn_date")
    .agg(
        F.round(F.sum("amount"), 2).alias("expected_revenue"),
        F.count("txn_id").alias("expected_txns")
    )
)

validation_join = (
    final_gold_df
    .join(silver_expected, on="txn_date")
    .withColumn("revenue_discrepancy", F.round(F.col("daily_revenue") - F.col("expected_revenue"), 2))
    .withColumn("count_discrepancy", F.col("transaction_count") - F.col("expected_txns"))
)

discrepancies = validation_join.filter((F.col("revenue_discrepancy") != 0) | (F.col("count_discrepancy") != 0)).count()

if discrepancies == 0:
    print("PROVEN: All Gold revenue figures exactly equal the sum of all valid Silver transactions!")
else:
    print(f"DISCREPANCY DETECTED: {discrepancies} dates failed validation.")
    display(validation_join.filter(F.col("revenue_discrepancy") != 0))

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 11 — Audit History, Time Travel & Watermark Advance
# MAGIC Inspect Delta transaction log, demonstrate before/after comparison, and advance watermark control table post-commit.

# COMMAND ----------
print("=== STEP 11: DELTA AUDIT & WATERMARK ADVANCE ===")
audit_mgr = DeltaAuditManager(config)

# Show Delta Commit History
history_df = audit_mgr.get_table_history(spark, config.GOLD_PATH)
display(history_df.select("version", "timestamp", "userId", "userName", "operation", "operationParameters"))

# Show Before vs After Comparison for Affected Dates
initial_gold_snapshot = spark.read.format("delta").option("versionAsOf", 0).load(config.GOLD_PATH)
comparison_report = corrector.compute_before_after_comparison(
    initial_gold_snapshot,
    final_gold_df,
    affected_dates_df
)

print("Sample Before/After Historical Revenue Corrections:")
display(comparison_report.limit(10))

# Watermark Control: Read -> Validate Successful Commit -> Advance Watermark
watermark_mgr = WatermarkManager(config)
current_watermark = watermark_mgr.get_watermark(spark, "gold_daily_revenue")
print(f"Pre-Execution Watermark: {current_watermark}")

# Advance Watermark ONLY after all downstream operations succeed
max_date = clean_silver_df.select(F.max("txn_date")).first()[0]
watermark_mgr.update_watermark(spark, "gold_daily_revenue", max_date, valid_silver_count)
print(f"Post-Execution Watermark successfully advanced to: {max_date} ({valid_silver_count} total records).")
