"""
Unit tests for Late Transaction Detection and Affected Historical Dates.
"""

import unittest
import csv
import datetime
from pathlib import Path


class TestLateTransactionDetection(unittest.TestCase):
    """
    Validates late transaction classification, lag computation, and affected historical date extraction.
    """

    @classmethod
    def setUpClass(cls):
        cls.csv_path = Path("data/Project_Dataset.csv")
        with open(cls.csv_path, mode="r", encoding="utf-8") as f:
            cls.raw_records = list(csv.DictReader(f))

    def test_exact_dataset_counts(self):
        """Verify total record count is 2,000."""
        self.assertEqual(len(self.raw_records), 2000)

    def test_late_vs_ontime_classification(self):
        """Verify late vs on-time split exactly matches 1,415 late and 585 on-time."""
        late_txns = []
        ontime_txns = []

        for r in self.raw_records:
            t_date = datetime.datetime.strptime(r["txn_date"], "%Y-%m-%d").date()
            i_date = datetime.datetime.strptime(r["ingestion_date"], "%Y-%m-%d").date()

            if i_date > t_date:
                late_txns.append(r)
            elif i_date == t_date:
                ontime_txns.append(r)
            else:
                self.fail(f"Invalid future ingestion date: {i_date} < {t_date}")

        self.assertEqual(len(late_txns), 1415, f"Expected 1415 late transactions, got {len(late_txns)}")
        self.assertEqual(len(ontime_txns), 585, f"Expected 585 on-time transactions, got {len(ontime_txns)}")
        self.assertEqual(len(late_txns) + len(ontime_txns), 2000)

    def test_affected_historical_dates(self):
        """Verify affected dates are strictly derived from distinct txn_date of late records."""
        late_dates = set()
        for r in self.raw_records:
            t_date = datetime.datetime.strptime(r["txn_date"], "%Y-%m-%d").date()
            i_date = datetime.datetime.strptime(r["ingestion_date"], "%Y-%m-%d").date()
            if i_date > t_date:
                late_dates.add(t_date)

        # All 60 historical dates should be affected or a subset
        self.assertGreater(len(late_dates), 0)
        self.assertLessEqual(len(late_dates), 60)

        # Verify no date outside 2024-01-01 to 2024-02-29 is included
        min_date = datetime.date(2024, 1, 1)
        max_date = datetime.date(2024, 2, 29)
        for d in late_dates:
            self.assertGreaterEqual(d, min_date)
            self.assertLessEqual(d, max_date)


if __name__ == "__main__":
    unittest.main()
