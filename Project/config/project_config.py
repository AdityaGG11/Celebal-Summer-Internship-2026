"""
Project Configuration for Late Transaction Handling & Historical Revenue Correction.

This module centralizes all table names, file paths, Delta paths, checkpoint paths,
and catalog configurations.

For Databricks Execution:
- In Unity Catalog enabled workspaces, use /Volumes/<catalog>/<schema>/<volume>/
- In legacy DBFS workspaces, use dbfs:/pipelines/late_transactions/
- For local testing, relative or absolute local directory paths are supported.
"""

import os
from dataclasses import dataclass

@dataclass
class PipelineConfig:
    # --------------------------------------------------------------------------
    # Catalog & Schema (Unity Catalog)
    # --------------------------------------------------------------------------
    CATALOG_NAME: str = "main"
    SCHEMA_NAME: str = "revenue_analytics"
    VOLUME_NAME: str = "transactions_raw"

    # Base path: Defaults to Unity Catalog Volume or DBFS path
    # Users can override BASE_DATA_PATH via environment variable if desired
    BASE_STORAGE_PATH: str = os.getenv(
        "PIPELINE_STORAGE_PATH", 
        "/Volumes/main/revenue_analytics/transactions_raw"
    )

    # --------------------------------------------------------------------------
    # Storage Paths
    # --------------------------------------------------------------------------
    # Path where raw incoming CSV files land (Auto Loader source)
    SOURCE_PATH: str = f"{BASE_STORAGE_PATH}/raw_csv"
    
    # Delta Table Storage Paths (External or Managed locations)
    BRONZE_PATH: str = f"{BASE_STORAGE_PATH}/delta/bronze_transactions"
    SILVER_PATH: str = f"{BASE_STORAGE_PATH}/delta/silver_transactions"
    GOLD_PATH: str = f"{BASE_STORAGE_PATH}/delta/gold_daily_revenue"
    
    # Quarantine / Error Storage Path
    QUARANTINE_PATH: str = f"{BASE_STORAGE_PATH}/delta/silver_quarantine"
    
    # Streaming Checkpoint & Schema Evolution Locations (Auto Loader)
    CHECKPOINT_BASE: str = f"{BASE_STORAGE_PATH}/checkpoints"
    BRONZE_CHECKPOINT: str = f"{CHECKPOINT_BASE}/bronze_autoloader"
    SCHEMA_LOCATION: str = f"{BASE_STORAGE_PATH}/schema_inference/bronze_transactions"
    
    # Watermark Control Table Location
    WATERMARK_PATH: str = f"{BASE_STORAGE_PATH}/delta/watermark_control"

    # --------------------------------------------------------------------------
    # Logical Metastore Table Names (Unity Catalog / Hive Metastore)
    # --------------------------------------------------------------------------
    BRONZE_TABLE: str = f"{CATALOG_NAME}.{SCHEMA_NAME}.bronze_transactions"
    SILVER_TABLE: str = f"{CATALOG_NAME}.{SCHEMA_NAME}.silver_transactions"
    GOLD_TABLE: str = f"{CATALOG_NAME}.{SCHEMA_NAME}.gold_daily_revenue"
    QUARANTINE_TABLE: str = f"{CATALOG_NAME}.{SCHEMA_NAME}.silver_quarantine"
    WATERMARK_TABLE: str = f"{CATALOG_NAME}.{SCHEMA_NAME}.watermark_control"

    # --------------------------------------------------------------------------
    # Pipeline Parameters
    # --------------------------------------------------------------------------
    CSV_DELIMITER: str = ","
    CSV_HEADER: bool = True
    MAX_FILES_PER_TRIGGER: int = 100
    AUTO_LOADER_FORMAT: str = "cloudFiles"

# Global default configuration instance
config = PipelineConfig()
