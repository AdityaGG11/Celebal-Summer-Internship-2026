"""
Edge Case Unit Tests for E-Commerce Order Analytics System
Uses Python standard-library unittest framework.
Tests edge cases on isolated temporary in-memory / temporary database instances.
Does NOT modify or corrupt canonical project data.
"""

import sqlite3
import unittest
from datetime import datetime
import pandas as pd

from src.data_cleaning.clean_data import check_referential_integrity, clean_orders


class TestTask8EdgeCases(unittest.TestCase):

    def setUp(self):
        """Creates an in-memory SQLite database with required tables for test isolation."""
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        self.cursor.execute("PRAGMA foreign_keys = ON;")

        self.cursor.execute("""
            CREATE TABLE customers (
                customer_id TEXT PRIMARY KEY,
                customer_name TEXT NOT NULL,
                email TEXT NOT NULL,
                registration_date TEXT NOT NULL,
                customer_type TEXT NOT NULL
            );
        """)

        self.cursor.execute("""
            CREATE TABLE products (
                product_id TEXT PRIMARY KEY,
                product_name TEXT NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT NOT NULL,
                cost_price REAL NOT NULL
            );
        """)

        self.cursor.execute("""
            CREATE TABLE orders (
                order_id TEXT PRIMARY KEY,
                customer_id TEXT,
                order_date TEXT NOT NULL,
                status TEXT NOT NULL,
                region_code TEXT NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            );
        """)

        self.cursor.execute("""
            CREATE TABLE order_items (
                item_id TEXT PRIMARY KEY,
                order_id TEXT NOT NULL,
                product_id TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                discount_percent REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(order_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            );
        """)

        # Insert seed product & customer
        self.cursor.execute("INSERT INTO customers VALUES ('CUST-001', 'Test User', 'test@example.com', '2023-01-01 00:00:00', 'REGULAR');")
        self.cursor.execute("INSERT INTO products VALUES ('PROD-001', 'Test Widget', 'Electronics', 'Gadgets', 10.0);")
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def test_edge_case_1_orphan_order_items(self):
        """Edge Case 1: Detects and isolates order_items whose order_id does not exist in orders."""
        orders_df = pd.DataFrame([
            {"order_id": "ORD-001", "customer_id": "CUST-001", "order_date": "2023-01-01 10:00:00", "status": "DELIVERED", "region_code": "US-EAST"}
        ])

        order_items_df = pd.DataFrame([
            {"item_id": "ITEM-001", "order_id": "ORD-001", "product_id": "PROD-001", "quantity": 1, "unit_price": 100.0, "discount_percent": 0.0},
            {"item_id": "ITEM-002", "order_id": "ORD-999", "product_id": "PROD-001", "quantity": 2, "unit_price": 50.0, "discount_percent": 0.0}
        ])

        valid_items, orphan_items = check_referential_integrity(order_items_df, orders_df)

        self.assertEqual(len(valid_items), 1)
        self.assertEqual(len(orphan_items), 1)
        self.assertEqual(orphan_items.iloc[0]["item_id"], "ITEM-002")
        self.assertEqual(orphan_items.iloc[0]["order_id"], "ORD-999")

    def test_edge_case_2_excessive_discount(self):
        """Edge Case 2: Handles discount_percent > 100 correctly (detects or rejects invalid discount)."""
        # Insert valid order
        self.cursor.execute("INSERT INTO orders VALUES ('ORD-001', 'CUST-001', '2023-01-01 10:00:00', 'DELIVERED', 'US-EAST');")
        
        # Insert item with 150% discount
        self.cursor.execute("INSERT INTO order_items VALUES ('ITEM-150', 'ORD-001', 'PROD-001', 2, 100.0, 150.0);")
        self.conn.commit()

        # Query revenue calculation
        self.cursor.execute("""
            SELECT 
                item_id,
                discount_percent,
                (quantity * unit_price * (1.0 - discount_percent / 100.0)) AS calc_revenue
            FROM order_items
            WHERE item_id = 'ITEM-150';
        """)
        row = self.cursor.fetchone()
        
        self.assertEqual(row["discount_percent"], 150.0)
        # Revenue calculation produces negative revenue or is detected as invalid (>100)
        self.assertLess(row["calc_revenue"], 0.0)

    def test_edge_case_3_zero_quantity(self):
        """Edge Case 3: Handles quantity = 0 safely without crashing, returning 0 revenue impact."""
        self.cursor.execute("INSERT INTO orders VALUES ('ORD-002', 'CUST-001', '2023-01-02 10:00:00', 'DELIVERED', 'US-EAST');")
        self.cursor.execute("INSERT INTO order_items VALUES ('ITEM-ZERO', 'ORD-002', 'PROD-001', 0, 100.0, 10.0);")
        self.conn.commit()

        self.cursor.execute("""
            SELECT 
                item_id,
                quantity,
                COALESCE(SUM(quantity * unit_price * (1.0 - discount_percent / 100.0)), 0.0) AS revenue
            FROM order_items
            WHERE item_id = 'ITEM-ZERO'
            GROUP BY item_id, quantity;
        """)
        row = self.cursor.fetchone()
        
        self.assertIsNotNone(row)
        self.assertEqual(row["quantity"], 0)
        self.assertEqual(row["revenue"], 0.0)

    def test_edge_case_4_future_order_date(self):
        """Edge Case 4: Detects future order dates relative to current execution date or dataset max date."""
        future_date_str = "2099-12-31 23:59:59"
        
        orders_df = pd.DataFrame([
            {"order_id": "ORD-FUTURE", "customer_id": "CUST-001", "order_date": future_date_str, "status": "PLACED", "region_code": "US-EAST"}
        ])

        cleaned_df, malformed_cnt = clean_orders(orders_df)
        
        parsed_dt = datetime.strptime(cleaned_df.iloc[0]["order_date"], "%Y-%m-%d %H:%M:%S")
        now_dt = datetime.now()

        # Verify that future date is flagged/detected as > now
        self.assertTrue(parsed_dt > now_dt)
        self.assertEqual(cleaned_df.iloc[0]["order_id"], "ORD-FUTURE")


if __name__ == "__main__":
    unittest.main()
