"""
Late Transaction Detection Layer.

Identifies transactions where ingestion_date > txn_date.
Extracts distinct affected historical dates for selective recalculation.
"""

from typing import Optional, Dict, Any, Tuple
from config.project_config import PipelineConfig, config

try:
    from pyspark.sql import SparkSession, DataFrame
    from pyspark.sql import functions as F
    PYSPARK_AVAILABLE = True
except ImportError:
    PYSPARK_AVAILABLE = False
    SparkSession = Any
    DataFrame = Any


class LateTransactionDetector:
    """
    Detects late-arriving transactions and extracts affected historical dates.
    """

    def __init__(self, cfg: Optional[PipelineConfig] = None):
        self.cfg = cfg or config

    def detect_late_transactions(self, silver_df: DataFrame) -> DataFrame:
        """
        Identifies all late transactions where ingestion_date > txn_date.
        Adds arrival_lag_days metric.
        """
        return (
            silver_df
            .filter(F.col("ingestion_date") > F.col("txn_date"))
            .withColumn("arrival_lag_days", F.datediff(F.col("ingestion_date"), F.col("txn_date")))
        )

    def detect_ontime_transactions(self, silver_df: DataFrame) -> DataFrame:
        """
        Identifies all on-time transactions where ingestion_date == txn_date.
        """
        return silver_df.filter(F.col("ingestion_date") == F.col("txn_date"))

    def get_affected_historical_dates(self, late_df: DataFrame) -> DataFrame:
        """
        Extracts distinct txn_date values that are impacted by late transactions.
        These are the exact dates that require surgical recalculation.
        """
        return (
            late_df
            .select("txn_date")
            .distinct()
            .orderBy("txn_date")
        )

    def get_metrics(self, silver_df: DataFrame) -> Dict[str, Any]:
        """
        Computes summary metrics regarding transaction arrival patterns.
        """
        total_count = silver_df.count()
        late_df = self.detect_late_transactions(silver_df)
        late_count = late_df.count()
        ontime_count = total_count - late_count
        affected_dates_df = self.get_affected_historical_dates(late_df)
        affected_dates_count = affected_dates_df.count()

        return {
            "total_transactions": total_count,
            "late_transactions": late_count,
            "ontime_transactions": ontime_count,
            "late_ratio_pct": round((late_count / total_count * 100), 2) if total_count > 0 else 0.0,
            "affected_dates_count": affected_dates_count,
        }
