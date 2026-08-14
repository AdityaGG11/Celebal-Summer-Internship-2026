"""
Data Quality Validation Framework.

Executes comprehensive checks on transactions across:
1. Null txn_id
2. Duplicate txn_id
3. Negative or zero amount values
4. Null or malformed transaction & ingestion dates
5. Logical consistency (e.g. txn_date <= ingestion_date for on-time/late classification)
"""

from typing import Optional, Dict, Any, List
from config.project_config import PipelineConfig, config

try:
    from pyspark.sql import SparkSession, DataFrame
    from pyspark.sql import functions as F
    PYSPARK_AVAILABLE = True
except ImportError:
    PYSPARK_AVAILABLE = False
    SparkSession = Any
    DataFrame = Any


class DataQualityChecker:
    """
    Runs automated data quality rules on Bronze and Silver transaction datasets.
    """

    def __init__(self, cfg: Optional[PipelineConfig] = None):
        self.cfg = cfg or config

    def check_dataset(self, df: DataFrame) -> Dict[str, Any]:
        """
        Runs comprehensive data quality validation suite on a Spark DataFrame.
        """
        if not PYSPARK_AVAILABLE:
            raise RuntimeError("PySpark required for DataQualityChecker.")

        total_records = df.count()
        if total_records == 0:
            return {
                "total_records": 0,
                "status": "EMPTY_DATASET",
                "checks": {}
            }

        # 1. Null checks
        null_txn_id = df.filter(F.col("txn_id").isNull()).count()
        null_user_id = df.filter(F.col("user_id").isNull()).count()
        null_txn_date = df.filter(F.col("txn_date").isNull()).count()
        null_ingestion_date = df.filter(F.col("ingestion_date").isNull()).count()
        null_amount = df.filter(F.col("amount").isNull()).count()

        # 2. Duplicate txn_id check
        duplicate_count = (
            df.groupBy("txn_id")
            .count()
            .filter(F.col("count") > 1)
            .count()
        )

        # 3. Negative / Zero amount check
        negative_amount_count = df.filter(F.col("amount") < 0).count()
        zero_amount_count = df.filter(F.col("amount") == 0).count()

        # 4. Inverted date check (ingestion_date < txn_date is physically impossible)
        inverted_date_count = df.filter(F.col("ingestion_date") < F.col("txn_date")).count()

        # Overall validity
        invalid_count = (
            null_txn_id +
            duplicate_count +
            negative_amount_count +
            zero_amount_count +
            null_txn_date +
            null_ingestion_date +
            inverted_date_count
        )

        valid_count = total_records - invalid_count

        return {
            "total_records": total_records,
            "valid_records": valid_count,
            "invalid_records": invalid_count,
            "null_txn_id_count": null_txn_id,
            "null_user_id_count": null_user_id,
            "duplicate_txn_id_count": duplicate_count,
            "negative_amount_count": negative_amount_count,
            "zero_amount_count": zero_amount_count,
            "null_txn_date_count": null_txn_date,
            "null_ingestion_date_count": null_ingestion_date,
            "inverted_date_count": inverted_date_count,
            "is_clean": invalid_count == 0
        }
