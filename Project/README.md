# Late Transaction Handling & Historical Revenue Correction

A Databricks-based **PySpark and Delta Lake data engineering pipeline** that addresses the late-arriving transaction problem using a **Medallion Architecture (Bronze → Silver → Gold)**.

The pipeline detects transactions that arrive after their actual transaction date, identifies the affected historical revenue dates, recalculates complete revenue for only those dates, and surgically updates the Gold Delta table using **Delta Lake MERGE**.

---

## 1. Executive Summary

In transactional systems such as e-commerce, banking, and payment processing, transactions may arrive after the date on which they actually occurred.

For example:

```text
Transaction Date : 2024-01-05
Ingestion Date   : 2024-01-12
```

The transaction belongs to the revenue of January 5 even though it was ingested on January 12.

If historical reports are not corrected, revenue for January 5 remains understated.

This project solves the problem through:

* Databricks Auto Loader for incremental Bronze ingestion.
* PySpark-based Silver transformation for cleansing, validation, typing, and deduplication.
* Gold daily revenue aggregation.
* Late transaction detection using `ingestion_date > txn_date`.
* Affected-date identification to determine which historical reports require correction.
* Selective revenue recalculation using all valid transactions for affected dates.
* Delta Lake MERGE to update only affected Gold records.
* Watermark control for incremental processing.
* Delta Lake history and Time Travel for auditability.
* Automated unit and pipeline-level validation.

The central engineering principle is:

> **Recalculate only what was affected instead of rebuilding the entire historical Gold dataset.**

---

## 2. Business Problem

### 2.1 The Problem

A transaction can be physically completed on one date but reach the data platform several days later.

The pipeline therefore distinguishes between:

```text
txn_date       = actual business transaction date
ingestion_date = date the transaction entered the platform
```

A transaction is considered late when:

```text
ingestion_date > txn_date
```

### Example

```text
txn_date       = 2024-01-08
ingestion_date = 2024-01-15
```

→ Late transaction
→ Revenue belongs to `2024-01-08`

A naive solution would recalculate the entire historical revenue table whenever late data arrives.

This is unnecessarily expensive and does not scale efficiently.

---

## 3. Solution

The implemented solution uses a Medallion Architecture:

```text
Raw CSV Files
      │
      ▼
┌──────────────────────────────┐
│           BRONZE             │
│    Raw Delta + Auto Loader   │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│            SILVER            │
│ Cleaned + Validated +        │
│ Deduplicated Transactions    │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       INITIAL GOLD           │
│    Initial Revenue Snapshot  │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│    LATE TRANSACTION DETECTION│
│     ingestion_date > txn_date│
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       AFFECTED DATES         │
│     DISTINCT txn_date values │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│    SELECTIVE RECALCULATION   │
│ ALL valid Silver transactions│
│      for affected dates only │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│         DELTA MERGE          │
│ target.txn_date =            │
│ source.txn_date              │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│     CORRECTED GOLD REVENUE   │
│       Audit + Time Travel    │
└──────────────────────────────┘
```

---

## 4. Medallion Architecture

### Bronze

Responsible for:

* Raw transaction ingestion
* Databricks Auto Loader
* CSV file processing
* Schema handling
* Checkpointing
* Source/file lineage metadata
* Delta Lake storage

The Bronze layer preserves the incoming transaction data before business-level transformations.

### Silver

Responsible for:

* Data type standardization
* Date normalization
* Transaction validation
* Duplicate detection
* Deterministic deduplication
* Invalid-record quarantine
* Amount validation

The trusted Silver dataset contains only valid transaction records.

### Gold

Responsible for:

* Daily revenue reporting
* Initial reporting snapshot
* Historical revenue correction
* Delta Lake MERGE

The primary business key is:

```text
txn_date
```

---

## 5. Late Transaction Correction Strategy

The correction process is deliberately selective.

### Step 1 — Detect Late Transactions

```text
ingestion_date > txn_date
```

### Step 2 — Extract Affected Dates

```text
late_transactions
        ↓
select txn_date
        ↓
distinct()
```

### Step 3 — Recalculate Affected Dates

For each affected date, revenue is recalculated using:

**ALL valid Silver transactions**

This includes:

* On-time transactions
* Late-arriving transactions

### Step 4 — MERGE into Gold

The corrected values are merged using:

```text
target.txn_date = source.txn_date
```

Conceptually:

```sql
WHEN MATCHED
    → UPDATE daily_revenue

WHEN NOT MATCHED
    → INSERT
```

Unaffected historical dates are not unnecessarily rewritten.

---

## 6. Initial Gold vs Corrected Gold

The project explicitly distinguishes between the initial reporting state and the final corrected state.

### Initial Gold

The initial reporting snapshot represents transactions available at the initial reporting point.

For the project demonstration:

```text
ingestion_date == txn_date
```

is used to represent the initial on-time reporting population.

### Corrected Gold

After late transactions are identified, affected historical dates are recalculated using all valid Silver transactions belonging to those dates.

Therefore:

```text
Initial Gold
     ↓
Late transactions detected
     ↓
Affected dates identified
     ↓
Complete historical revenue recalculated
     ↓
Delta MERGE
     ↓
Corrected Gold
```

---

## 7. Dataset

The pipeline operates on:

```text
data/Project_Dataset.csv
```

### Dataset Statistics

| Metric                      |                   Value |
| --------------------------- | ----------------------: |
| Total Transactions          |                   2,000 |
| Unique Users                |                     400 |
| Unique Transaction Dates    |                      60 |
| Transaction Date Range      | 2024-01-01 → 2024-02-29 |
| Maximum Ingestion Date      |              2024-03-14 |
| On-Time Transactions        |                     585 |
| Late Transactions           |                   1,415 |
| Late Transaction Percentage |                  70.75% |
| Affected Historical Dates   |                      60 |
| Null Values                 |                       0 |
| Duplicate Transaction IDs   |                       0 |
| Negative Amounts            |                       0 |
| Zero Amounts                |                       0 |

### Dataset Schema

| Column           | Type          | Description                           |
| ---------------- | ------------- | ------------------------------------- |
| `txn_id`         | BIGINT        | Unique transaction identifier         |
| `user_id`        | BIGINT        | Customer/user identifier              |
| `txn_date`       | DATE          | Actual transaction date               |
| `amount`         | DECIMAL(18,2) | Transaction amount                    |
| `ingestion_date` | DATE          | Date transaction entered the platform |

---

## 8. Technology Stack

| Component            | Technology             | Purpose                             |
| -------------------- | ---------------------- | ----------------------------------- |
| Data Platform        | Databricks             | Pipeline execution                  |
| Processing Engine    | Apache Spark           | Distributed processing              |
| Processing Framework | PySpark                | Transformations and business logic  |
| Storage              | Delta Lake             | ACID storage, MERGE and Time Travel |
| Ingestion            | Databricks Auto Loader | Incremental file ingestion          |
| Query                | Spark SQL              | Validation and analytical queries   |
| Language             | Python                 | Pipeline implementation             |
| Input                | CSV                    | Source transaction data             |
| Output               | Delta Tables           | Bronze, Silver and Gold layers      |
| Testing              | Python `unittest`      | Automated unit testing              |

---

## 9. Project Structure

```text
Project/
│
├── README.md
├── PROJECT_REQUIREMENTS.md
├── IMPLEMENTATION_NOTES.md
├── TESTING.md
│
├── data/
│   └── Project_Dataset.csv
│
├── config/
│   ├── __init__.py
│   └── project_config.py
│
├── src/
│   ├── __init__.py
│   ├── bronze.py
│   ├── silver.py
│   ├── gold.py
│   ├── late_transactions.py
│   ├── historical_correction.py
│   ├── data_quality.py
│   ├── watermark.py
│   ├── audit.py
│   └── generate_dataset.py
│
├── notebooks/
│   ├── 01_bronze_ingestion.py
│   ├── 02_silver_transformation.py
│   ├── 03_gold_aggregation.py
│   ├── 04_late_transaction_detection.py
│   ├── 05_historical_correction.py
│   ├── 06_data_quality.py
│   ├── 07_watermark.py
│   └── 08_end_to_end_demo.py
│
├── sql/
│   ├── create_tables.sql
│   ├── validation_queries.sql
│   └── audit_queries.sql
│
└── tests/
    ├── __init__.py
    ├── test_data_quality.py
    ├── test_late_transactions.py
    ├── test_revenue_recalculation.py
    ├── test_expected_results.py
    └── local_pipeline_test.py
```

---

## 10. Source Code Components

| File                           | Responsibility                                          |
| ------------------------------ | ------------------------------------------------------- |
| `src/bronze.py`                | Auto Loader ingestion and Bronze Delta processing       |
| `src/silver.py`                | Cleansing, validation, quarantine and deduplication     |
| `src/gold.py`                  | Initial Gold revenue aggregation                        |
| `src/late_transactions.py`     | Late transaction detection and affected-date extraction |
| `src/historical_correction.py` | Selective revenue recalculation and Delta MERGE         |
| `src/data_quality.py`          | Data-quality and invariant checks                       |
| `src/watermark.py`             | Watermark control table management                      |
| `src/audit.py`                 | Delta history and time-travel utilities                 |
| `src/generate_dataset.py`      | Deterministic dataset generation/validation             |

---

## 11. Databricks Notebooks

The notebooks provide a step-by-step implementation and demonstration.

| Notebook                           | Purpose                           |
| ---------------------------------- | --------------------------------- |
| `01_bronze_ingestion.py`           | Auto Loader → Bronze              |
| `02_silver_transformation.py`      | Silver cleansing and validation   |
| `03_gold_aggregation.py`           | Initial Gold revenue              |
| `04_late_transaction_detection.py` | Late transaction detection        |
| `05_historical_correction.py`      | Selective recalculation + MERGE   |
| `06_data_quality.py`               | Data-quality validation           |
| `07_watermark.py`                  | Watermark control                 |
| `08_end_to_end_demo.py`            | Complete end-to-end demonstration |

The recommended entry point for demonstrating the complete solution is:

```text
notebooks/08_end_to_end_demo.py
```

---

## 12. Databricks Setup

The project is designed to run on a Databricks environment with Delta Lake support.

### Step 1 — Import the Repository

Clone or import this repository into Databricks Repos or the Databricks workspace.

### Step 2 — Create Unity Catalog Resources

If Unity Catalog is available and the user has the required privileges:

```sql
CREATE CATALOG IF NOT EXISTS main;

CREATE SCHEMA IF NOT EXISTS main.revenue_analytics;

CREATE VOLUME IF NOT EXISTS main.revenue_analytics.transactions_raw;
```

Upload:

```text
data/Project_Dataset.csv
```

to:

```text
/Volumes/main/revenue_analytics/transactions_raw/raw_csv/
```

### Step 3 — Configure Paths

Update:

```text
config/project_config.py
```

as required by the Databricks environment.

Example:

```python
CATALOG_NAME = "main"
SCHEMA_NAME = "revenue_analytics"
VOLUME_NAME = "transactions_raw"

BASE_STORAGE_PATH = (
    "/Volumes/main/revenue_analytics/transactions_raw"
)
```

### Step 4 — Run the End-to-End Demonstration

Open:

```text
notebooks/08_end_to_end_demo.py
```

and execute it on a compatible Databricks cluster.

---

## 13. Local Testing

The project contains a Python unit-test suite and a local pipeline validation harness.

### Run Unit Tests

```bash
python -m unittest discover tests -v
```

### Run Pipeline Validation

```bash
python tests/local_pipeline_test.py
```

---

## 14. Test Results

The current implementation has been validated using:

### Unit Tests

```text
20 / 20 PASSED
```

### Pipeline-Level Tests

```text
10 / 10 PASSED
```

The pipeline validation covers:

* Dataset loading
* Type conversion
* Data quality
* Late transaction detection
* Affected-date identification
* Revenue recalculation
* Delta MERGE simulation
* Unaffected-date preservation
* Idempotency
* End-to-end revenue invariant

---

## 15. Validation Results

The implemented validation pipeline reports:

```text
Total Transactions       : 2,000
On-Time Transactions     : 585
Late Transactions        : 1,415
Affected Dates           : 60

Initial Revenue          : $294,592.50
Late Revenue             : $673,201.38
Final Corrected Revenue  : $967,793.88
```

The final validation invariant is:

```text
Final Gold Revenue
        =
SUM(valid Silver transaction amounts)
```

with the implemented validation result:

```text
$967,793.88 = $967,793.88
```

---

## 16. Operational Invariants

The project is designed to maintain the following invariants.

### 16.1 Selective Recalculation

Only historical dates affected by late transactions are recalculated.

### 16.2 Complete Revenue Recalculation

For an affected date `D`:

```text
Corrected Revenue(D)
=
SUM(amount)
for ALL valid Silver transactions
where txn_date = D
```

This includes both on-time and late transactions.

### 16.3 Surgical MERGE

Gold is updated using:

```text
target.txn_date = source.txn_date
```

rather than rebuilding the complete Gold table.

### 16.4 Idempotency

Running the correction again without new data should produce the same Gold state.

### 16.5 Revenue Consistency

The final corrected Gold revenue must equal the corresponding revenue calculated from valid Silver transactions.

---

## 17. Watermark Control

The project maintains a Delta-based watermark control table containing:

```text
table_name
last_processed_date
```

The intended processing lifecycle is:

```text
Read Watermark
      ↓
Process Required Data
      ↓
Complete Downstream Processing
      ↓
Successful Commit
      ↓
Update Watermark
```

The watermark is advanced only after successful downstream processing.

This provides a foundation for incremental execution and controlled reprocessing.

---

## 18. Auditability

Delta Lake provides transaction history and Time Travel capabilities.

The project includes:

```text
sql/audit_queries.sql
```

for inspecting:

* Delta transaction history
* Table versions
* Before/after states
* Historical corrections

Useful Delta operations include:

```sql
DESCRIBE HISTORY <gold_table>;
```

and Delta Time Travel queries using a previous table version where available.

This allows the historical correction to be inspected as an auditable data change.

---

## 19. Engineering Benefits

### Surgical Corrections

Only affected historical dates are recalculated.

### Reduced Processing

The pipeline avoids unnecessary full historical recomputation.

### Data Quality

Silver-layer validation prevents invalid records from directly affecting business reporting.

### ACID Updates

Delta Lake provides transactional guarantees for Gold-layer MERGE operations.

### Incremental Ingestion

Auto Loader supports incremental file discovery and checkpointed streaming ingestion.

### Auditability

Delta History and Time Travel provide visibility into table changes.

### Scalability

PySpark and Databricks provide distributed processing capabilities suitable for significantly larger datasets.

### Idempotency

Repeated correction runs without new data do not change the final Gold state.

---

## 20. Scope

This project focuses on the data engineering problem of:

> **Detecting late-arriving transactions and selectively correcting historical daily revenue.**

The following are outside the primary scope:

* Custom web UI
* Real-time dashboards
* Machine learning
* External APIs
* Multi-source ingestion
* Enterprise authentication
* Complex orchestration infrastructure
* Production CI/CD deployment
* Large-scale performance benchmarking

The project prioritizes correctness, incremental processing, data quality, selective historical correction, and auditability.

---

## 21. Limitations

The supplied dataset contains only 2,000 transactions and is therefore primarily intended for functional demonstration and validation rather than large-scale performance benchmarking.

Local automated tests validate the pipeline's business logic and expected results. Databricks-specific capabilities such as actual Auto Loader streaming, Delta MERGE execution, and Delta Time Travel should be demonstrated in the Databricks environment.

The project does not include a custom frontend because the core requirement is a data engineering pipeline rather than a web application.

---

## 22. Future Scope

Potential extensions include:

* Databricks Workflows for scheduled execution
* Power BI/Tableau integration
* Operational monitoring dashboards
* Automated data-quality alerts
* Additional transaction sources
* Event-time based incremental processing
* Transaction-delay analytics
* Automated anomaly detection
* CI/CD deployment
* Enterprise observability and alerting

---

## 23. Conclusion

The **Late Transaction Handling & Historical Revenue Correction** pipeline demonstrates how modern data engineering technologies can be used to maintain accurate historical revenue in the presence of delayed transaction ingestion.

The solution combines:

```text
Databricks
    +
PySpark
    +
Delta Lake
    +
Auto Loader
    +
Medallion Architecture
```

to create a layered and auditable transaction-processing pipeline.

The core mechanism is selective historical correction:

```text
Late Transaction
      ↓
Affected Historical Date
      ↓
Recalculate ALL Valid Transactions
      ↓
Delta MERGE
      ↓
Corrected Gold Revenue
```

This avoids unnecessary full-table recomputation while ensuring that historical revenue reflects all available valid transactions.

The implemented validation suite reports:

```text
20 / 20 unit tests passed
10 / 10 pipeline tests passed
```

with:

```text
2,000 total transactions
1,415 late transactions
60 affected dates
$967,793.88 final corrected revenue
```

The project is therefore structured as a **Databricks-ready data engineering solution for late-arriving transaction handling and selective historical revenue correction**.

---

## Author

**Aditya**

**Celebal Summer Internship 2026**

**Project:** Late Transaction Handling & Historical Revenue Correction
