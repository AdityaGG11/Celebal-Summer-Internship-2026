"""
Bronze Layer: Raw Ingestion via Databricks Auto Loader.

Ingests raw CSV transactions into the Bronze Delta table.
Preserves raw structure without business cleansing.
"""

from typing import Optional, Dict, Any
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


class BronzeIngestion:
    """
    Handles streaming ingestion of raw CSV files into Delta Bronze layer using
    Databricks Auto Loader (cloudFiles).
    """

    def __init__(self, cfg: Optional[PipelineConfig] = None):
        self.cfg = cfg or config

    @property
    def raw_schema(self) -> "T.StructType":
        """
        Defines the expected raw schema for transaction files.
        """
        if not PYSPARK_AVAILABLE:
            return None
        return T.StructType([
            T.StructField("txn_id", T.StringType(), True),
            T.StructField("user_id", T.StringType(), True),
            T.StructField("txn_date", T.StringType(), True),
            T.StructField("amount", T.StringType(), True),
            T.StructField("ingestion_date", T.StringType(), True),
        ])

    def read_autoloader_stream(self, spark: SparkSession) -> DataFrame:
        """
        Sets up Auto Loader streaming DataFrame on incoming CSV directory.
        Uses cloudFiles with schema inference and evolution support.
        """
        if not PYSPARK_AVAILABLE:
            raise RuntimeError("PySpark is required to run Auto Loader streaming.")

        return (
            spark.readStream
            .format(self.cfg.AUTO_LOADER_FORMAT)
            .option("cloudFiles.format", "csv")
            .option("cloudFiles.schemaLocation", self.cfg.SCHEMA_LOCATION)
            .option("cloudFiles.inferColumnTypes", "false")  # Keep as raw strings in Bronze
            .option("cloudFiles.maxFilesPerTrigger", self.cfg.MAX_FILES_PER_TRIGGER)
            .option("header", "true")
            .option("delimiter", self.cfg.CSV_DELIMITER)
            .schema(self.raw_schema)
            .load(self.cfg.SOURCE_PATH)
            .withColumn("_bronze_ingested_at", F.current_timestamp())
            .withColumn("_source_file", F.input_file_name())
        )

    def write_autoloader_stream(
        self, 
        df: DataFrame, 
        trigger_available_now: bool = True
    ) -> Any:
        """
        Writes the Auto Loader stream to the Bronze Delta table with checkpointing.
        """
        if not PYSPARK_AVAILABLE:
            raise RuntimeError("PySpark is required to execute streaming write.")

        writer = (
            df.writeStream
            .format("delta")
            .outputMode("append")
            .option("checkpointLocation", self.cfg.BRONZE_CHECKPOINT)
        )

        if trigger_available_now:
            writer = writer.trigger(availableNow=True)

        # Write to path or table
        return writer.start(self.cfg.BRONZE_PATH)

    def ingest_batch(self, spark: SparkSession, source_csv_path: Optional[str] = None) -> DataFrame:
        """
        Batch ingestion alternative for non-streaming environments or initial loads.
        Reads CSV directly and appends to Bronze Delta location.
        """
        if not PYSPARK_AVAILABLE:
            raise RuntimeError("PySpark is required for batch ingestion.")

        csv_path = source_csv_path or f"{self.cfg.SOURCE_PATH}/*.csv"
        raw_df = (
            spark.read
            .format("csv")
            .option("header", "true")
            .option("delimiter", self.cfg.CSV_DELIMITER)
            .schema(self.raw_schema)
            .load(csv_path)
            .withColumn("_bronze_ingested_at", F.current_timestamp())
            .withColumn("_source_file", F.input_file_name())
        )

        raw_df.write.format("delta").mode("append").save(self.cfg.BRONZE_PATH)
        return raw_df
