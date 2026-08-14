"""
Watermark & Control Table Management Layer.

Maintains a Delta Lake control table to track high-watermarks for incremental processing.
Ensures that the watermark is only advanced AFTER a pipeline stage successfully completes.
"""

from typing import Optional, Dict, Any
from datetime import date, datetime
from config.project_config import PipelineConfig, config

try:
    from pyspark.sql import SparkSession, DataFrame
    from pyspark.sql import functions as F
    from pyspark.sql import types as T
    from delta.tables import DeltaTable
    PYSPARK_AVAILABLE = True
except ImportError:
    PYSPARK_AVAILABLE = False
    SparkSession = Any
    DataFrame = Any
    DeltaTable = Any


class WatermarkManager:
    """
    Manages the watermark control table in Delta Lake for tracking incremental ingestion.
    """

    def __init__(self, cfg: Optional[PipelineConfig] = None):
        self.cfg = cfg or config

    @property
    def schema(self) -> "T.StructType":
        if not PYSPARK_AVAILABLE:
            return None
        return T.StructType([
            T.StructField("table_name", T.StringType(), False),
            T.StructField("last_processed_date", T.DateType(), True),
            T.StructField("last_processed_timestamp", T.TimestampType(), True),
            T.StructField("records_processed", T.LongType(), True),
        ])

    def initialize_control_table(self, spark: SparkSession) -> None:
        """
        Initializes the watermark control Delta table if it does not already exist.
        """
        if not PYSPARK_AVAILABLE:
            raise RuntimeError("PySpark required for WatermarkManager.")

        # Check if table or path exists
        try:
            spark.read.format("delta").load(self.cfg.WATERMARK_PATH)
        except Exception:
            # Create empty control table
            empty_df = spark.createDataFrame([], self.schema)
            empty_df.write.format("delta").mode("overwrite").save(self.cfg.WATERMARK_PATH)

    def get_watermark(self, spark: SparkSession, table_name: str) -> Optional[date]:
        """
        Retrieves the last_processed_date for the given table.
        Returns None if table has not been processed yet.
        """
        if not PYSPARK_AVAILABLE:
            raise RuntimeError("PySpark required for WatermarkManager.")

        self.initialize_control_table(spark)
        df = spark.read.format("delta").load(self.cfg.WATERMARK_PATH)
        row = (
            df.filter(F.col("table_name") == table_name)
            .select("last_processed_date")
            .first()
        )
        return row["last_processed_date"] if row else None

    def update_watermark(
        self, 
        spark: SparkSession, 
        table_name: str, 
        last_processed_date: date,
        records_processed: int
    ) -> None:
        """
        Surgically updates or inserts the watermark record in the Delta control table.
        MUST only be invoked after pipeline operations have successfully committed.
        """
        if not PYSPARK_AVAILABLE:
            raise RuntimeError("PySpark required for WatermarkManager.")

        self.initialize_control_table(spark)
        watermark_delta = DeltaTable.forPath(spark, self.cfg.WATERMARK_PATH)

        update_record = spark.createDataFrame(
            [(table_name, last_processed_date, datetime.now(), int(records_processed))],
            self.schema
        )

        (
            watermark_delta.alias("target")
            .merge(
                source=update_record.alias("source"),
                condition="target.table_name = source.table_name"
            )
            .whenMatchedUpdate(set={
                "last_processed_date": "source.last_processed_date",
                "last_processed_timestamp": "source.last_processed_timestamp",
                "records_processed": "source.records_processed"
            })
            .whenNotMatchedInsert(values={
                "table_name": "source.table_name",
                "last_processed_date": "source.last_processed_date",
                "last_processed_timestamp": "source.last_processed_timestamp",
                "records_processed": "source.records_processed"
            })
            .execute()
        )
