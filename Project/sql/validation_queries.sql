-- =============================================================================
-- Validation Queries for Data Quality, Late Transactions & Revenue Reconciliation
-- =============================================================================

USE main.revenue_analytics;

-- -----------------------------------------------------------------------------
-- 1. Data Quality Checks on Bronze & Silver
-- -----------------------------------------------------------------------------

-- 1.1 Null checks
SELECT 
    COUNT(*) AS total_bronze_records,
    COUNT(CASE WHEN txn_id IS NULL OR TRIM(txn_id) = '' THEN 1 END) AS null_txn_id_count,
    COUNT(CASE WHEN user_id IS NULL OR TRIM(user_id) = '' THEN 1 END) AS null_user_id_count,
    COUNT(CASE WHEN txn_date IS NULL OR TRIM(txn_date) = '' THEN 1 END) AS null_txn_date_count,
    COUNT(CASE WHEN amount IS NULL OR TRIM(amount) = '' THEN 1 END) AS null_amount_count
FROM bronze_transactions;

-- 1.2 Duplicate Transaction IDs in Bronze
SELECT 
    txn_id, 
    COUNT(*) AS occurrence_count
FROM bronze_transactions
GROUP BY txn_id
HAVING COUNT(*) > 1;

-- 1.3 Silver Quality Verification (Must return 0 records)
SELECT 
    COUNT(*) AS invalid_silver_records
FROM silver_transactions
WHERE txn_id IS NULL 
   OR user_id IS NULL 
   OR txn_date IS NULL 
   OR ingestion_date IS NULL 
   OR amount <= 0;

-- -----------------------------------------------------------------------------
-- 2. Late Transaction Detection Queries
-- -----------------------------------------------------------------------------

-- 2.1 Total Late vs On-Time Breakdown
SELECT 
    CASE 
        WHEN ingestion_date > txn_date THEN 'LATE'
        WHEN ingestion_date = txn_date THEN 'ON_TIME'
        ELSE 'INVALID_FUTURE_INGESTION'
    END AS transaction_arrival_type,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount), 2) AS total_amount,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS pct_of_total
FROM silver_transactions
GROUP BY 1;

-- 2.2 Affected Historical Dates Summary
SELECT 
    txn_date,
    COUNT(*) AS late_txn_count,
    ROUND(SUM(amount), 2) AS late_revenue_added,
    MIN(ingestion_date) AS first_late_arrival,
    MAX(ingestion_date) AS last_late_arrival,
    MAX(DATEDIFF(ingestion_date, txn_date)) AS max_arrival_lag_days
FROM silver_transactions
WHERE ingestion_date > txn_date
GROUP BY txn_date
ORDER BY txn_date;

-- -----------------------------------------------------------------------------
-- 3. Revenue Reconciliation Query (Mathematical Invariant Verification)
-- -----------------------------------------------------------------------------
-- Proves that Gold daily_revenue EXACTLY matches SUM(amount) of all valid Silver rows
SELECT 
    g.txn_date,
    g.daily_revenue AS gold_revenue,
    g.transaction_count AS gold_txn_count,
    s.silver_sum_amount,
    s.silver_txn_count,
    ROUND(g.daily_revenue - s.silver_sum_amount, 2) AS revenue_discrepancy
FROM gold_daily_revenue g
JOIN (
    SELECT 
        txn_date,
        ROUND(SUM(amount), 2) AS silver_sum_amount,
        COUNT(*) AS silver_txn_count
    FROM silver_transactions
    GROUP BY txn_date
) s ON g.txn_date = s.txn_date
WHERE g.daily_revenue != s.silver_sum_amount
ORDER BY g.txn_date;
