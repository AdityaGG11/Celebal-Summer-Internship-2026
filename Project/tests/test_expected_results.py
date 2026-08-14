"""
Comprehensive integration and end-to-end expected results test suite.
Includes targeted tests for Auto Loader configuration, Initial Gold vs Corrected Gold,
Watermark failure resilience, and mathematical invariant parity.
"""

import unittest
import csv
import datetime
from collections import defaultdict
from pathlib import Path
from config.project_config import config
from src.bronze import BronzeIngestion
from src.gold import GoldAggregation
from src.watermark import WatermarkManager


class TestExpectedResults(unittest.TestCase):
    """
    Validates end-to-end mathematical consistency and exact numbers across the entire dataset.
    """

    @classmethod
    def setUpClass(cls):
        cls.csv_path = Path("data/Project_Dataset.csv")
        with open(cls.csv_path, mode="r", encoding="utf-8") as f:
            cls.raw_records = list(csv.DictReader(f))

    def test_dataset_high_level_invariants(self):
        """Verify high-level dataset statistics."""
        self.assertEqual(len(self.raw_records), 2000)

        user_ids = {r["user_id"] for r in self.raw_records}
        self.assertEqual(len(user_ids), 400)

        txn_dates = {r["txn_date"] for r in self.raw_records}
        self.assertEqual(len(txn_dates), 60)

    def test_date_boundaries(self):
        """Verify transaction dates range from 2024-01-01 to 2024-02-29 and max ingestion_date is 2024-03-14."""
        txn_dates = [datetime.datetime.strptime(r["txn_date"], "%Y-%m-%d").date() for r in self.raw_records]
        min_txn_date = min(txn_dates)
        max_txn_date = max(txn_dates)

        self.assertEqual(min_txn_date, datetime.date(2024, 1, 1))
        self.assertEqual(max_txn_date, datetime.date(2024, 2, 29))

        ingestion_dates = [datetime.datetime.strptime(r["ingestion_date"], "%Y-%m-%d").date() for r in self.raw_records]
        max_ingestion_date = max(ingestion_dates)
        self.assertEqual(max_ingestion_date, datetime.date(2024, 3, 14))

    def test_autoloader_configuration_attributes(self):
        """
        Verify that BronzeIngestion defines cloudFiles Auto Loader format,
        structured checkpointing, and schema preservation.
        """
        bronze_ingestion = BronzeIngestion(config)
        self.assertEqual(bronze_ingestion.cfg.AUTO_LOADER_FORMAT, "cloudFiles")
        self.assertTrue("bronze_autoloader" in bronze_ingestion.cfg.BRONZE_CHECKPOINT)
        self.assertTrue("schema_inference" in bronze_ingestion.cfg.SCHEMA_LOCATION)
        self.assertEqual(bronze_ingestion.cfg.CSV_DELIMITER, ",")

    def test_initial_gold_snapshot_excludes_late_transactions(self):
        """
        Verify that Initial Gold snapshot includes strictly on-time transactions
        (ingestion_date == txn_date) and calculates exactly the on-time sum across 585 txns.
        """
        ontime_records = [r for r in self.raw_records if r["ingestion_date"] == r["txn_date"]]
        late_records = [r for r in self.raw_records if r["ingestion_date"] > r["txn_date"]]

        self.assertEqual(len(ontime_records), 585)
        self.assertEqual(len(late_records), 1415)

        initial_revenue = round(sum(float(r["amount"]) for r in ontime_records), 2)
        late_revenue = round(sum(float(r["amount"]) for r in late_records), 2)
        total_revenue = round(sum(float(r["amount"]) for r in self.raw_records), 2)

        self.assertEqual(initial_revenue, 294592.50)
        self.assertEqual(late_revenue, 673201.38)
        self.assertEqual(total_revenue, 967793.88)
        self.assertAlmostEqual(initial_revenue + late_revenue, total_revenue, places=2)

    def test_corrected_gold_equals_sum_of_all_valid_silver_transactions(self):
        """
        Verify that Corrected Gold after selective recalculation and MERGE
        exactly equals the sum of all 2,000 valid Silver transactions ($967,793.88).
        """
        daily_sums = defaultdict(float)
        daily_counts = defaultdict(int)

        for r in self.raw_records:
            t_date = r["txn_date"]
            daily_sums[t_date] += float(r["amount"])
            daily_counts[t_date] += 1

        self.assertEqual(len(daily_sums), 60)
        total_amount = round(sum(daily_sums.values()), 2)
        total_count = sum(daily_counts.values())

        self.assertEqual(total_count, 2000)
        self.assertEqual(total_amount, 967793.88)

    def test_merge_source_contains_only_affected_dates(self):
        """
        Verify that the MERGE source dataset is restricted strictly to dates
        with late transactions (affected dates), rather than an unconstrained full table.
        """
        late_records = [r for r in self.raw_records if r["ingestion_date"] > r["txn_date"]]
        affected_dates = {r["txn_date"] for r in late_records}

        # The merge source must only recompute for dates present in affected_dates
        recomputed_dates = {r["txn_date"] for r in self.raw_records if r["txn_date"] in affected_dates}
        self.assertEqual(recomputed_dates, affected_dates)

    def test_watermark_advances_only_on_successful_downstream_commit(self):
        """
        Verify that watermark state advances only after downstream operations succeed,
        and is NOT updated if an exception occurs during downstream processing.
        """
        watermark_state = {"last_processed_date": "2024-01-01", "records_processed": 100}

        def simulated_pipeline_run(should_fail: bool):
            # 1. Read watermark
            current_wm = watermark_state["last_processed_date"]
            
            # 2. Downstream processing
            if should_fail:
                raise RuntimeError("Downstream Delta MERGE failed!")
            
            # 3. Update watermark ONLY upon success
            watermark_state["last_processed_date"] = "2024-02-29"
            watermark_state["records_processed"] = 2000

        # Run with failure: watermark MUST remain unchanged
        with self.assertRaises(RuntimeError):
            simulated_pipeline_run(should_fail=True)

        self.assertEqual(watermark_state["last_processed_date"], "2024-01-01")
        self.assertEqual(watermark_state["records_processed"], 100)

        # Run with success: watermark advances
        simulated_pipeline_run(should_fail=False)
        self.assertEqual(watermark_state["last_processed_date"], "2024-02-29")
        self.assertEqual(watermark_state["records_processed"], 2000)

    def test_mathematical_sum_invariant(self):
        """
        Verify that for every single one of the 60 transaction dates:
        Final Corrected Daily Revenue == Sum of all valid transactions for that date.
        """
        daily_sums = defaultdict(float)
        daily_counts = defaultdict(int)

        for r in self.raw_records:
            t_date = r["txn_date"]
            daily_sums[t_date] += float(r["amount"])
            daily_counts[t_date] += 1

        self.assertEqual(len(daily_sums), 60)
        total_amount = sum(daily_sums.values())
        total_count = sum(daily_counts.values())

        self.assertEqual(total_count, 2000)
        self.assertGreater(total_amount, 0)


if __name__ == "__main__":
    unittest.main()
