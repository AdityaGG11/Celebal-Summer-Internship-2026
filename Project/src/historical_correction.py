"""
Historical Revenue Correction Layer: Selective Recalculation & Delta Lake MERGE.

Identifies affected historical dates, recalculates full daily revenue using ALL valid
transactions (on-time + late) for those dates only, and applies surgical updates
to the Gold Delta table via Delta Lake MERGE.
"""

from typing import Optional, Dict, Any, Tuple
from config.project_config import PipelineConfig, config

try:
    from pyspark.sql import SparkSession, DataFrame
    from pyspark.sql import functions as F
    from pyspark.sql import types as T
    from delta.tables import DeltaTable
    DELTA_AVAILABLE = True
except ImportError:
    DELTA_AVAILABLE = False
    SparkSession = Any
    DataFrame = Any
    DeltaTable = Any


class HistoricalRevenueCorrector:
    """
    Executes selective recalculation of affected historical revenue records and
    merges corrections into the Gold Delta table.
    """

    def __init__(self, cfg: Optional[PipelineConfig] = None):
        self.cfg = cfg or config

    def recalculate_affected_revenue(
        self, 
        silver_df: DataFrame, 
        affected_dates_df: DataFrame
    ) -> DataFrame:
        """
        Recalculates daily revenue ONLY for affected dates.
        CRITICAL: Includes ALL valid transactions (both on-time and late) for those dates.
        """
        recalculated_df = (
            silver_df
            .join(affected_dates_df, on="txn_date", how="inner")
            .groupBy("txn_date")
            .agg(
                F.round(F.sum("amount").cast(T.DecimalType(18, 2)), 2).alias("daily_revenue"),
                F.count("txn_id").alias("transaction_count")
            )
            .withColumn("_gold_updated_at", F.current_timestamp())
        )
        return recalculated_df

    def merge_into_gold(
        self, 
        spark: SparkSession, 
        recalculated_df: DataFrame,
        gold_table_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Performs Delta Lake MERGE into the Gold Delta table.
        Updates existing dates with corrected revenue and inserts any new dates.
        """
        if not DELTA_AVAILABLE:
            raise RuntimeError("Delta Lake library is required for Delta MERGE execution.")

        target_path = gold_table_path or self.cfg.GOLD_PATH
        gold_delta_table = DeltaTable.forPath(spark, target_path)

        # Execute Delta MERGE
        (
            gold_delta_table.alias("target")
            .merge(
                source=recalculated_df.alias("source"),
                condition="target.txn_date = source.txn_date"
            )
            .whenMatchedUpdate(set={
                "daily_revenue": "source.daily_revenue",
                "transaction_count": "source.transaction_count",
                "_gold_updated_at": "source._gold_updated_at"
            })
            .whenNotMatchedInsert(values={
                "txn_date": "source.txn_date",
                "daily_revenue": "source.daily_revenue",
                "transaction_count": "source.transaction_count",
                "_gold_updated_at": "source._gold_updated_at"
            })
            .execute()
        )

        return {
            "status": "SUCCESS",
            "merged_records_count": recalculated_df.count(),
            "target_path": target_path
        }

    def compute_before_after_comparison(
        self,
        gold_before_df: DataFrame,
        gold_after_df: DataFrame,
        affected_dates_df: DataFrame
    ) -> DataFrame:
        """
        Generates a clear audit comparison showing:
        txn_date | old_revenue | corrected_revenue | revenue_diff | old_txns | corrected_txns | txn_diff
        """
        before_sub = (
            gold_before_df
            .select(
                F.col("txn_date"),
                F.col("daily_revenue").alias("old_revenue"),
                F.col("transaction_count").alias("old_txns")
            )
        )

        after_sub = (
            gold_after_df
            .select(
                F.col("txn_date"),
                F.col("daily_revenue").alias("corrected_revenue"),
                F.col("transaction_count").alias("corrected_txns")
            )
        )

        comparison_df = (
            affected_dates_df
            .join(before_sub, on="txn_date", how="left")
            .join(after_sub, on="txn_date", how="inner")
            .withColumn("revenue_diff", F.round(F.col("corrected_revenue") - F.coalesce(F.col("old_revenue"), F.lit(0.0)), 2))
            .withColumn("txn_diff", F.col("corrected_txns") - F.coalesce(F.col("old_txns"), F.lit(0)))
            .orderBy("txn_date")
        )

        return comparison_df
