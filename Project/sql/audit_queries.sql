-- =============================================================================
-- Audit & Delta Lake Time Travel Queries
-- Demonstrates Delta History, Versioning, and Surgical MERGE Validation
-- =============================================================================

USE main.revenue_analytics;

-- -----------------------------------------------------------------------------
-- 1. Delta Table History Inspection
-- -----------------------------------------------------------------------------
-- Shows all transaction commits (WRITE, MERGE, OPTIMIZE)
DESCRIBE HISTORY gold_daily_revenue;

-- Detailed history of Watermark Control table
DESCRIBE HISTORY watermark_control;

-- -----------------------------------------------------------------------------
-- 2. Time Travel Queries: Compare Before vs After Correction
-- -----------------------------------------------------------------------------

-- Query Initial Gold State (Version 0 - before late transaction correction)
SELECT 
    txn_date,
    daily_revenue AS initial_revenue,
    transaction_count AS initial_txns,
    _gold_updated_at AS initial_timestamp
FROM gold_daily_revenue VERSION AS OF 0
ORDER BY txn_date;

-- Query Corrected Gold State (Latest Version - after selective Delta MERGE)
SELECT 
    txn_date,
    daily_revenue AS corrected_revenue,
    transaction_count AS corrected_txns,
    _gold_updated_at AS corrected_timestamp
FROM gold_daily_revenue
ORDER BY txn_date;

-- -----------------------------------------------------------------------------
-- 3. Surgical Time-Travel Delta Diff Report
-- -----------------------------------------------------------------------------
-- Highlights only the dates whose revenue changed between Version 0 and Latest
SELECT 
    curr.txn_date,
    init.daily_revenue AS baseline_revenue_v0,
    curr.daily_revenue AS corrected_revenue_latest,
    ROUND(curr.daily_revenue - COALESCE(init.daily_revenue, 0), 2) AS revenue_correction_delta,
    init.transaction_count AS baseline_txns_v0,
    curr.transaction_count AS corrected_txns_latest,
    (curr.transaction_count - COALESCE(init.transaction_count, 0)) AS late_txns_incorporated
FROM gold_daily_revenue curr
LEFT JOIN (SELECT * FROM gold_daily_revenue VERSION AS OF 0) init
    ON curr.txn_date = init.txn_date
WHERE curr.daily_revenue != init.daily_revenue
   OR init.txn_date IS NULL
ORDER BY curr.txn_date;

-- -----------------------------------------------------------------------------
-- 4. Watermark Audit
-- -----------------------------------------------------------------------------
SELECT 
    table_name,
    last_processed_date,
    last_processed_timestamp,
    records_processed
FROM watermark_control;
