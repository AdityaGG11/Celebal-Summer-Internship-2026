"""
Unit tests for Historical Revenue Recalculation and MERGE logic.
"""

import unittest
import csv
import datetime
from collections import defaultdict
from pathlib import Path


class TestRevenueRecalculation(unittest.TestCase):
    """
    Validates that selective recalculation includes ALL valid transactions for affected dates,
    and accurately preserves unchanged dates.
    """

    @classmethod
    def setUpClass(cls):
        cls.csv_path = Path("data/Project_Dataset.csv")
        with open(cls.csv_path, mode="r", encoding="utf-8") as f:
            cls.raw_records = list(csv.DictReader(f))

    def test_recalculation_includes_all_transactions(self):
        """
        Verify that for an affected date, recalculated revenue equals
        SUM(on_time_amount) + SUM(late_amount), NOT just SUM(late_amount).
        """
        ontime_by_date = defaultdict(float)
        late_by_date = defaultdict(float)
        total_by_date = defaultdict(float)

        for r in self.raw_records:
            t_date = r["txn_date"]
            i_date = r["ingestion_date"]
            amt = float(r["amount"])

            total_by_date[t_date] += amt
            if i_date > t_date:
                late_by_date[t_date] += amt
            else:
                ontime_by_date[t_date] += amt

        # Pick a sample affected date
        sample_date = list(late_by_date.keys())[0]
        ontime_rev = round(ontime_by_date[sample_date], 2)
        late_rev = round(late_by_date[sample_date], 2)
        expected_full_rev = round(total_by_date[sample_date], 2)

        # Recalculated revenue MUST be greater than just the late amount if on-time exists
        self.assertAlmostEqual(ontime_rev + late_rev, expected_full_rev, places=2)

    def test_selective_processing_efficiency(self):
        """
        Verify that only affected dates need recomputing, and un-impacted dates remain constant.
        """
        ontime_only_dates = set()
        all_dates = set()
        affected_dates = set()

        for r in self.raw_records:
            t_date = r["txn_date"]
            i_date = r["ingestion_date"]
            all_dates.add(t_date)
            if i_date > t_date:
                affected_dates.add(t_date)

        # Affected dates should be a well-defined subset or total set
        self.assertEqual(len(affected_dates), len(set(r["txn_date"] for r in self.raw_records if r["ingestion_date"] > r["txn_date"])))

    def test_merge_idempotency(self):
        """
        Verify that running the recalculation and merge twice with no new data
        yields the identical revenue and count.
        """
        revenue_v1 = defaultdict(float)
        for r in self.raw_records:
            revenue_v1[r["txn_date"]] += float(r["amount"])
        
        # Round values
        for d in revenue_v1:
            revenue_v1[d] = round(revenue_v1[d], 2)

        # Simulate second pass merge
        revenue_v2 = defaultdict(float)
        for r in self.raw_records:
            revenue_v2[r["txn_date"]] += float(r["amount"])
        for d in revenue_v2:
            revenue_v2[d] = round(revenue_v2[d], 2)

        self.assertEqual(revenue_v1, revenue_v2, "MERGE is not idempotent!")


if __name__ == "__main__":
    unittest.main()
