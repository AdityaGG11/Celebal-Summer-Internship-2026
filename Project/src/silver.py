"""
Silver Layer: Data Cleaning, Type Enforcement, Validation, and Deterministic Deduplication.

Transforms raw Bronze data into high-quality Silver transactions.
Routes invalid records to quarantine.
"""

from typing import Optional, Tuple, Any
from config.project_config import PipelineConfig, config

try:
    from pyspark.sql import SparkSession, DataFrame, Window
    from pyspark.sql import functions as F
    from pyspark.sql import types as T
    PYSPARK_AVAILABLE = True
except ImportError:
    PYSPARK_AVAILABLE = False
    SparkSession = Any
    DataFrame = Any


class SilverTransformation:
    """
    Cleans, validates, type-casts, and deduplicates transactions from Bronze to Silver.
    """

    def __init__(self, cfg: Optional[PipelineConfig] = None):
        self.cfg = cfg or config

    def clean_and_cast(self, bronze_df: DataFrame) -> DataFrame:
        """
        Performs explicit schema type casting and trims string fields.
        """
        return (
            bronze_df
            .withColumn("txn_id", F.trim(F.col("txn_id")).cast(T.LongType()))
            .withColumn("user_id", F.trim(F.col("user_id")).cast(T.LongType()))
            .withColumn("txn_date", F.to_date(F.trim(F.col("txn_date")), "yyyy-MM-dd"))
            .withColumn("ingestion_date", F.to_date(F.trim(F.col("ingestion_date")), "yyyy-MM-dd"))
            .withColumn("amount", F.round(F.trim(F.col("amount")).cast(T.DecimalType(18, 2)), 2))
        )

    def validate_and_quarantine(self, df: DataFrame) -> Tuple[DataFrame, DataFrame]:
        """
        Applies validation rules:
        - txn_id IS NOT NULL
        - amount IS NOT NULL AND amount > 0
        - txn_date IS NOT NULL
        - ingestion_date IS NOT NULL
        
        Returns:
            (valid_df, quarantine_df)
        """
        # Define invalid conditions
        invalid_condition = (
            F.col("txn_id").isNull() |
            F.col("user_id").isNull() |
            F.col("txn_date").isNull() |
            F.col("ingestion_date").isNull() |
            F.col("amount").isNull() |
            (F.col("amount") <= 0)
        )

        quarantine_df = df.filter(invalid_condition).withColumn(
            "_quarantine_reason",
            F.when(F.col("txn_id").isNull(), "NULL_TXN_ID")
            .when(F.col("user_id").isNull(), "NULL_USER_ID")
            .when(F.col("txn_date").isNull(), "INVALID_TXN_DATE")
            .when(F.col("ingestion_date").isNull(), "INVALID_INGESTION_DATE")
            .when(F.col("amount").isNull() | (F.col("amount") <= 0), "INVALID_AMOUNT")
            .otherwise("OTHER_VALIDATION_FAILURE")
        ).withColumn("_quarantined_at", F.current_timestamp())

        valid_df = df.filter(~invalid_condition)

        return valid_df, quarantine_df

    def deduplicate(self, valid_df: DataFrame) -> DataFrame:
        """
        Performs deterministic deduplication on txn_id.
        If duplicate txn_ids exist, keeps the latest ingested record with highest amount.
        """
        window_spec = Window.partitionBy("txn_id").orderBy(
            F.col("ingestion_date").desc(),
            F.col("amount").desc()
        )

        deduped_df = (
            valid_df
            .withColumn("_row_num", F.row_number().over(window_spec))
            .filter(F.col("_row_num") == 1)
            .drop("_row_num")
        )

        return deduped_df

    def process(self, spark: SparkSession, bronze_df: Optional[DataFrame] = None) -> Tuple[DataFrame, DataFrame]:
        """
        Full Silver execution workflow:
        1. Read from Bronze Delta (if not passed).
        2. Clean and cast types.
        3. Quarantine invalid rows.
        4. Deduplicate valid rows.
        5. Write valid to Silver Delta and quarantined to Quarantine Delta.
        """
        if not PYSPARK_AVAILABLE:
            raise RuntimeError("PySpark required for Silver processing.")

        if bronze_df is None:
            bronze_df = spark.read.format("delta").load(self.cfg.BRONZE_PATH)

        typed_df = self.clean_and_cast(bronze_df)
        valid_df, quarantine_df = self.validate_and_quarantine(typed_df)
        clean_silver_df = self.deduplicate(valid_df)

        # Write clean silver data
        (
            clean_silver_df.write
            .format("delta")
            .mode("overwrite")  # Or append / merge based on streaming orchestration
            .save(self.cfg.SILVER_PATH)
        )

        # Write quarantine records if any exist
        if quarantine_df.count() > 0:
            (
                quarantine_df.write
                .format("delta")
                .mode("append")
                .save(self.cfg.QUARANTINE_PATH)
            )

        return clean_silver_df, quarantine_df
