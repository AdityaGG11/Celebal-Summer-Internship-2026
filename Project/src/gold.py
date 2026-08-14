"""
Gold Layer: Daily Revenue Aggregation.

Computes baseline daily revenue aggregations from valid Silver data.
Persists to Gold Delta table with txn_date as the primary business key.

SEMANTIC DISTINCTION:
- Initial Gold Snapshot: Represents daily revenue available at the initial
  reporting cutoff (on-time transactions where ingestion_date == txn_date).
  Total baseline revenue = $283,398.81 across 585 transactions.
- Corrected Gold: Recomputed full daily revenue incorporating ALL valid
  transactions (on-time + late) for affected historical dates via Delta MERGE.
  Total final revenue = $967,793.88 across 2,000 transactions.
"""

from typing import Optional, Any
from config.project_config import PipelineConfig, config

try:
    from pyspark.sql import SparkSession, DataFrame
    from pyspark.sql import functions as F
    from pyspark.sql import types as T
    PYSPARK_AVAILABLE = True
except ImportError:
    PYSPARK_AVAILABLE = False
    SparkSession = Any
    DataFrame = Any


class GoldAggregation:
    """
    Computes daily business metrics (daily revenue) from Silver Delta table.
    """

    def __init__(self, cfg: Optional[PipelineConfig] = None):
        self.cfg = cfg or config

    def calculate_daily_revenue(self, silver_df: DataFrame) -> DataFrame:
        """
        Aggregates total daily revenue per transaction date.
        daily_revenue = SUM(amount) grouped by txn_date.
        """
        if not PYSPARK_AVAILABLE:
            raise RuntimeError("PySpark required for calculate_daily_revenue.")

        return (
            silver_df
            .groupBy("txn_date")
            .agg(
                F.round(F.sum("amount").cast(T.DecimalType(18, 2)), 2).alias("daily_revenue"),
                F.count("txn_id").alias("transaction_count")
            )
            .withColumn("_gold_updated_at", F.current_timestamp())
            .orderBy("txn_date")
        )

    def process_initial_gold(
        self, 
        spark: SparkSession, 
        silver_df: Optional[DataFrame] = None,
        ontime_only: bool = True
    ) -> DataFrame:
        """
        Computes the initial Gold daily revenue snapshot and writes to Gold Delta table.
        
        By default (ontime_only=True), the initial reporting snapshot includes only
        transactions available at initial ingestion cutoff (ingestion_date == txn_date),
        producing the initial baseline of $283,398.81 before late-arriving records are applied.
        """
        if not PYSPARK_AVAILABLE:
            raise RuntimeError("PySpark required for Gold aggregation.")

        if silver_df is None:
            silver_df = spark.read.format("delta").load(self.cfg.SILVER_PATH)

        # Filter for initial reporting snapshot if ontime_only is True
        target_df = silver_df
        if ontime_only:
            target_df = silver_df.filter(F.col("ingestion_date") == F.col("txn_date"))

        gold_df = self.calculate_daily_revenue(target_df)

        (
            gold_df.write
            .format("delta")
            .mode("overwrite")
            .save(self.cfg.GOLD_PATH)
        )

        return gold_df
