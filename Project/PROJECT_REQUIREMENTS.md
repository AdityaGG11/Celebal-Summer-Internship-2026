# Project Requirements & Acceptance Criteria

## Project Title: Late Transaction Handling & Historical Revenue Correction

### 1. Business Objective
When financial or transactional data arrives after its actual transaction date (`ingestion_date > txn_date`), the pipeline must:
1. Detect late transactions and identify the specific affected historical dates.
2. Selectively recalculate full daily revenue for those dates using **ALL valid transactions** (on-time + late).
3. Surgically update only the affected records in the Gold Delta table using **Delta Lake MERGE**.

---

### 2. Technical Stack Requirements
* **Databricks**: Unity Catalog / DBFS
* **Apache Spark / PySpark**: 3.4+ / 3.5+
* **Delta Lake**: 3.x with ACID transactions, Time Travel, and Delta MERGE
* **Databricks Auto Loader**: `cloudFiles` format with checkpointing and schema inference
* **Medallion Architecture**: Bronze (raw), Silver (clean/dedup/quarantine), Gold (daily aggregates)
* **Control Layer**: Delta watermark control table

---

### 3. Acceptance Criteria Checklist

| ID | Requirement | Implementation Module | Status |
|:---|:---|:---|:---:|
| **AC-01** | CSV dataset loads successfully with 2,000 transactions across 60 dates | `src/generate_dataset.py`, `tests/` | **PASSED** |
| **AC-02** | Bronze Delta table exists with raw schema preservation | `src/bronze.py`, `sql/create_tables.sql` | **PASSED** |
| **AC-03** | Bronze uses Databricks Auto Loader (`cloudFiles`) with checkpointing | `src/bronze.py`, `notebooks/01_bronze_ingestion.py` | **PASSED** |
| **AC-04** | Silver Delta table performs explicit type casting | `src/silver.py`, `notebooks/02_silver_transformation.py` | **PASSED** |
| **AC-05** | Silver validates null `txn_id`, negative amounts, and bad dates | `src/silver.py`, `src/data_quality.py` | **PASSED** |
| **AC-06** | Silver quarantines invalid records into `silver_quarantine` table | `src/silver.py`, `sql/create_tables.sql` | **PASSED** |
| **AC-07** | Silver deterministically deduplicates `txn_id` via windowing | `src/silver.py` | **PASSED** |
| **AC-08** | Gold Delta table computes baseline daily revenue (`SUM(amount)`) | `src/gold.py`, `notebooks/03_gold_aggregation.py` | **PASSED** |
| **AC-09** | Late transactions detected using `ingestion_date > txn_date` | `src/late_transactions.py` | **PASSED** |
| **AC-10** | Affected historical dates extracted as `DISTINCT txn_date` | `src/late_transactions.py` | **PASSED** |
| **AC-11** | Recalculation is selective (only affected dates recalculated) | `src/historical_correction.py` | **PASSED** |
| **AC-12** | Recalculation includes ALL valid transactions for affected dates | `src/historical_correction.py` | **PASSED** |
| **AC-13** | Delta MERGE surgically updates Gold matching on `txn_date` | `src/historical_correction.py` | **PASSED** |
| **AC-14** | Unaffected historical dates remain untouched and preserved | `src/historical_correction.py`, `tests/` | **PASSED** |
| **AC-15** | Watermark control table tracks execution high-watermarks | `src/watermark.py`, `notebooks/07_watermark.py` | **PASSED** |
| **AC-16** | Watermark is updated ONLY after successful pipeline completion | `src/watermark.py` | **PASSED** |
| **AC-17** | Data quality framework generates structured validation report | `src/data_quality.py` | **PASSED** |
| **AC-18** | Delta history & Time Travel auditability implemented | `src/audit.py`, `sql/audit_queries.sql` | **PASSED** |
| **AC-19** | Master 11-step End-to-End demonstration notebook exists | `notebooks/08_end_to_end_demo.py` | **PASSED** |
| **AC-20** | Full test suite passes with zero errors | `tests/`, `tests/local_pipeline_test.py` | **PASSED** |

---

### 4. Non-Functional Requirements
- **Performance**: Selective recalculation avoids $O(N)$ full table scans by joining only with affected dates.
- **Idempotency**: Rerunning the recalculation and MERGE with the same dataset causes zero state divergence.
- **Modularity**: Separation of concerns between Bronze, Silver, Gold, Late Detection, Correction, Quality, Watermark, and Audit.
- **Maintainability**: Clean Python code adhering to PEP 8 standards with no unnecessary external framework dependencies.
