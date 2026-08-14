"""
Unit tests for Data Quality rules and validation checks.
Tests can run locally with Python stdlib as well as with PySpark if available.
"""

import unittest
import csv
import datetime
from pathlib import Path


class TestDataQuality(unittest.TestCase):
    """
    Tests for schema adherence, null checks, duplicate rejection, and quarantine rules.
    """

    @classmethod
    def setUpClass(cls):
        cls.csv_path = Path("data/Project_Dataset.csv")
        if not cls.csv_path.exists():
            raise FileNotFoundError("Project_Dataset.csv must exist in data/ before running tests.")
        
        with open(cls.csv_path, mode="r", encoding="utf-8") as f:
            cls.raw_records = list(csv.DictReader(f))

    def test_schema_and_columns_exist(self):
        """Test 1: Verify all expected columns exist in dataset."""
        expected_fields = {"txn_id", "user_id", "txn_date", "amount", "ingestion_date"}
        if len(self.raw_records) > 0:
            actual_fields = set(self.raw_records[0].keys())
            self.assertEqual(expected_fields, actual_fields, f"Columns mismatch: {actual_fields}")

    def test_no_null_transaction_ids(self):
        """Test 2: Verify zero null or empty txn_id records."""
        null_txn_ids = [
            r for r in self.raw_records 
            if r.get("txn_id") is None or r.get("txn_id").strip() == ""
        ]
        self.assertEqual(len(null_txn_ids), 0, f"Found {len(null_txn_ids)} null txn_ids.")

    def test_no_duplicate_transaction_ids(self):
        """Test 3: Verify all transaction IDs are globally unique."""
        txn_ids = [r["txn_id"] for r in self.raw_records]
        unique_txn_ids = set(txn_ids)
        self.assertEqual(len(txn_ids), len(unique_txn_ids), "Duplicate txn_ids detected!")

    def test_positive_amounts_only(self):
        """Test 4: Verify all transaction amounts are strictly positive (> 0)."""
        invalid_amounts = []
        for r in self.raw_records:
            try:
                amt = float(r["amount"])
                if amt <= 0:
                    invalid_amounts.append(r)
            except ValueError:
                invalid_amounts.append(r)
        
        self.assertEqual(len(invalid_amounts), 0, f"Found {len(invalid_amounts)} non-positive amounts.")

    def test_valid_date_formats(self):
        """Test 5: Verify txn_date and ingestion_date parse to valid YYYY-MM-DD dates."""
        for r in self.raw_records:
            try:
                t_date = datetime.datetime.strptime(r["txn_date"], "%Y-%m-%d").date()
                i_date = datetime.datetime.strptime(r["ingestion_date"], "%Y-%m-%d").date()
            except ValueError as e:
                self.fail(f"Invalid date format in row {r}: {e}")
            
            # Logical invariant: Ingestion cannot happen BEFORE the transaction physically occurred
            self.assertGreaterEqual(
                i_date, 
                t_date, 
                f"Ingestion date {i_date} is before transaction date {t_date} for txn_id {r['txn_id']}"
            )

    def test_quarantine_rule_simulation(self):
        """Test 6: Verify quarantine logic properly catches synthetic bad records."""
        synthetic_bad_rows = [
            {"txn_id": "", "user_id": "1001", "txn_date": "2024-01-01", "amount": "100.00", "ingestion_date": "2024-01-01"}, # Null ID
            {"txn_id": "9999", "user_id": "1001", "txn_date": "2024-01-01", "amount": "-50.00", "ingestion_date": "2024-01-01"}, # Negative amount
            {"txn_id": "9998", "user_id": "1001", "txn_date": "invalid-date", "amount": "10.00", "ingestion_date": "2024-01-01"}, # Bad date
        ]

        def is_valid(row):
            if not row.get("txn_id") or row["txn_id"].strip() == "":
                return False, "NULL_TXN_ID"
            try:
                if float(row["amount"]) <= 0:
                    return False, "INVALID_AMOUNT"
                datetime.datetime.strptime(row["txn_date"], "%Y-%m-%d")
                datetime.datetime.strptime(row["ingestion_date"], "%Y-%m-%d")
            except Exception:
                return False, "PARSE_ERROR"
            return True, "VALID"

        for bad_row in synthetic_bad_rows:
            valid, reason = is_valid(bad_row)
            self.assertFalse(valid, f"Row should have been quarantined: {bad_row}")
            self.assertNotEqual(reason, "VALID")


if __name__ == "__main__":
    unittest.main()
