"""
Auditability & Delta Lake Time Travel Layer.

Provides utilities for querying Delta transaction logs (DESCRIBE HISTORY),
performing time travel queries, and generating version diff reports.
"""

from typing import Optional, Dict, Any, List
from config.project_config import PipelineConfig, config

try:
    from pyspark.sql import SparkSession, DataFrame
    from pyspark.sql import functions as F
    from delta.tables import DeltaTable
    PYSPARK_AVAILABLE = True
except ImportError:
    PYSPARK_AVAILABLE = False
    SparkSession = Any
    DataFrame = Any
    DeltaTable = Any


class DeltaAuditManager:
    """
    Manages Delta Lake audit history and time-travel inspections.
    """

    def __init__(self, cfg: Optional[PipelineConfig] = None):
        self.cfg = cfg or config

    def get_table_history(self, spark: SparkSession, table_path_or_name: Optional[str] = None) -> DataFrame:
        """
        Retrieves full Delta Lake commit history for the specified table.
        """
        if not PYSPARK_AVAILABLE:
            raise RuntimeError("PySpark & Delta Lake required for DeltaAuditManager.")

        target = table_path_or_name or self.cfg.GOLD_PATH
        if target.startswith("/") or target.startswith("dbfs:"):
            delta_table = DeltaTable.forPath(spark, target)
        else:
            delta_table = DeltaTable.forName(spark, target)

        return delta_table.history()

    def get_version_snapshot(
        self, 
        spark: SparkSession, 
        version: int, 
        table_path: Optional[str] = None
    ) -> DataFrame:
        """
        Reads a specific historical version snapshot of the Delta table using time travel.
        """
        if not PYSPARK_AVAILABLE:
            raise RuntimeError("PySpark required for time travel queries.")

        path = table_path or self.cfg.GOLD_PATH
        return (
            spark.read
            .format("delta")
            .option("versionAsOf", version)
            .load(path)
        )

    def compare_versions(
        self,
        spark: SparkSession,
        version_a: int,
        version_b: int,
        key_column: str = "txn_date",
        metric_column: str = "daily_revenue",
        table_path: Optional[str] = None
    ) -> DataFrame:
        """
        Compares two historical snapshots of a Delta table and returns the delta.
        """
        df_a = self.get_version_snapshot(spark, version_a, table_path).select(
            F.col(key_column),
            F.col(metric_column).alias(f"{metric_column}_v{version_a}")
        )

        df_b = self.get_version_snapshot(spark, version_b, table_path).select(
            F.col(key_column),
            F.col(metric_column).alias(f"{metric_column}_v{version_b}")
        )

        return (
            df_a.join(df_b, on=key_column, how="full_outer")
            .withColumn(
                "metric_difference",
                F.round(F.col(f"{metric_column}_v{version_b}") - F.col(f"{metric_column}_v{version_a}"), 2)
            )
            .orderBy(key_column)
        )
