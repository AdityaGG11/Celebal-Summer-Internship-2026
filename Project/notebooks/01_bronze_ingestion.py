# Databricks notebook source
# MAGIC %md
# MAGIC # 01 - Bronze Layer Ingestion via Databricks Auto Loader
# MAGIC 
# MAGIC ### Objective:
# MAGIC Ingest raw CSV transaction files using **Databricks Auto Loader (`cloudFiles`)** into the **Bronze Delta table**.
# MAGIC 
# MAGIC ### Key Principles:
# MAGIC - Schema inference & evolution support with `cloudFiles.schemaLocation`.
# MAGIC - Preserves complete raw data without applying destructive business cleansing.
# MAGIC - Appends file metadata (`_source_file`, `_bronze_ingested_at`).
# MAGIC - Exactly-once streaming ingestion with structured checkpoints.

# COMMAND ----------
# MAGIC %md
# MAGIC ### Step 1: Import Dependencies & Configuration

# COMMAND ----------
import sys
import os
sys.path.append(os.path.abspath(".."))

from pyspark.sql import functions as F
from pyspark.sql import types as T
from config.project_config import config
from src.bronze import BronzeIngestion

print(f"Auto Loader Source Path: {config.SOURCE_PATH}")
print(f"Bronze Delta Target Path: {config.BRONZE_PATH}")
print(f"Checkpoint Path:          {config.BRONZE_CHECKPOINT}")

# COMMAND ----------
# MAGIC %md
# MAGIC ### Step 2: Initialize Bronze Ingestion & Define Schema

# COMMAND ----------
bronze_ingestion = BronzeIngestion(config)
raw_schema = bronze_ingestion.raw_schema
print("Expected Raw Schema:")
for field in raw_schema.fields:
    print(f" - {field.name}: {field.dataType}")

# COMMAND ----------
# MAGIC %md
# MAGIC ### Step 3: Configure Auto Loader Stream (cloudFiles)

# COMMAND ----------
# Auto Loader readStream definition
bronze_stream_df = bronze_ingestion.read_autoloader_stream(spark)

# Display sample of streaming schema
bronze_stream_df.printSchema()

# COMMAND ----------
# MAGIC %md
# MAGIC ### Step 4: Execute Auto Loader Ingestion (Trigger AvailableNow)

# COMMAND ----------
# Write stream to Bronze Delta Table with Checkpointing
streaming_query = bronze_ingestion.write_autoloader_stream(
    bronze_stream_df, 
    trigger_available_now=True
)

streaming_query.awaitTermination()
print(f"Bronze Ingestion Stream completed successfully.")

# COMMAND ----------
# MAGIC %md
# MAGIC ### Step 5: Verify Bronze Delta Table Content

# COMMAND ----------
# Read persisted Bronze Delta table
bronze_df = spark.read.format("delta").load(config.BRONZE_PATH)
bronze_count = bronze_df.count()

print(f"Total Bronze Records Ingested: {bronze_count}")
display(bronze_df.limit(10))
