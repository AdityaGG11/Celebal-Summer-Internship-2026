-- =============================================================================
-- DDL Definitions for Medallion Architecture & Control Tables
-- Target: Databricks Unity Catalog / Spark SQL Delta Lake
-- =============================================================================

-- 1. Create Schema / Database if not exists
CREATE SCHEMA IF NOT EXISTS main.revenue_analytics
COMMENT 'Schema for Late Transaction Ingestion and Historical Revenue Correction';

USE main.revenue_analytics;

-- 2. Bronze Layer: Raw Transactions Table (Ingested via Auto Loader)
CREATE TABLE IF NOT EXISTS main.revenue_analytics.bronze_transactions (
    txn_id STRING COMMENT 'Raw transaction ID',
    user_id STRING COMMENT 'Raw customer/user ID',
    txn_date STRING COMMENT 'Raw transaction date string',
    amount STRING COMMENT 'Raw transaction amount string',
    ingestion_date STRING COMMENT 'Raw ingestion date string',
    _bronze_ingested_at TIMESTAMP COMMENT 'Metadata timestamp when Auto Loader ingested record',
    _source_file STRING COMMENT 'Metadata path of origin CSV file'
)
USING DELTA
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
)
COMMENT 'Bronze raw transactions table ingested via Auto Loader';

-- 3. Silver Layer: Clean, Validated, Type-Casted & Deduplicated Transactions
CREATE TABLE IF NOT EXISTS main.revenue_analytics.silver_transactions (
    txn_id BIGINT NOT NULL COMMENT 'Unique transaction identifier (Validated & Deduplicated)',
    user_id BIGINT NOT NULL COMMENT 'Unique user identifier',
    txn_date DATE NOT NULL COMMENT 'Actual business transaction date',
    amount DECIMAL(18, 2) NOT NULL COMMENT 'Transaction amount in currency units (Positive > 0)',
    ingestion_date DATE NOT NULL COMMENT 'Date record was ingested into system',
    _bronze_ingested_at TIMESTAMP COMMENT 'Origin ingestion timestamp from Bronze',
    _source_file STRING COMMENT 'Source file path'
)
USING DELTA
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true'
)
COMMENT 'Silver curated transactions table';

-- 4. Silver Quarantine Table (For invalid records violating business constraints)
CREATE TABLE IF NOT EXISTS main.revenue_analytics.silver_quarantine (
    txn_id STRING,
    user_id STRING,
    txn_date STRING,
    amount STRING,
    ingestion_date STRING,
    _quarantine_reason STRING COMMENT 'Reason why record failed validation (NULL_ID, NEGATIVE_AMT, etc.)',
    _quarantined_at TIMESTAMP COMMENT 'Timestamp when record was quarantined'
)
USING DELTA
COMMENT 'Silver quarantine table for bad/corrupt transaction records';

-- 5. Gold Layer: Aggregated Daily Revenue
CREATE TABLE IF NOT EXISTS main.revenue_analytics.gold_daily_revenue (
    txn_date DATE NOT NULL COMMENT 'Business transaction date (Primary Key)',
    daily_revenue DECIMAL(18, 2) NOT NULL COMMENT 'Total aggregated revenue for the date (SUM of valid txns)',
    transaction_count BIGINT NOT NULL COMMENT 'Total count of transactions contributing to daily revenue',
    _gold_updated_at TIMESTAMP COMMENT 'Timestamp when record was created or updated via Delta MERGE'
)
USING DELTA
TBLPROPERTIES (
    'delta.feature.allowColumnDefaults' = 'supported'
)
COMMENT 'Gold aggregated daily revenue table updated surgically via Delta MERGE';

-- 6. Control Layer: Watermark Control Table
CREATE TABLE IF NOT EXISTS main.revenue_analytics.watermark_control (
    table_name STRING NOT NULL COMMENT 'Name of downstream target table being tracked',
    last_processed_date DATE COMMENT 'High-watermark transaction/ingestion date processed',
    last_processed_timestamp TIMESTAMP COMMENT 'Timestamp when pipeline completed successfully',
    records_processed BIGINT COMMENT 'Total count of records committed in last batch'
)
USING DELTA
COMMENT 'Control table maintaining execution high-watermarks for incremental pipelines';
