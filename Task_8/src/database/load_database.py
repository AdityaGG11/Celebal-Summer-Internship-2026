"""
Database Loader Module for E-Commerce Order Analytics System
Creates SQLite database database/ecommerce.db, creates table schema with foreign keys,
and loads data from data/cleaned/ CSV files using sqlite3.
Executes PRAGMA integrity_check and PRAGMA foreign_key_check.
"""

import csv
import sqlite3
from pathlib import Path


def load_database(base_dir: Path = None):
    if base_dir is None:
        base_dir = Path(__file__).resolve().parent.parent.parent

    cleaned_dir = base_dir / "data" / "cleaned"
    db_dir = base_dir / "database"
    db_dir.mkdir(parents=True, exist_ok=True)
    db_path = db_dir / "ecommerce.db"

    # Remove existing db file for deterministic reload
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Create tables
    cursor.execute("""
        CREATE TABLE customers (
            customer_id TEXT PRIMARY KEY,
            customer_name TEXT NOT NULL,
            email TEXT NOT NULL,
            registration_date TEXT NOT NULL,
            customer_type TEXT NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE products (
            product_id TEXT PRIMARY KEY,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            subcategory TEXT NOT NULL,
            cost_price REAL NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE orders (
            order_id TEXT PRIMARY KEY,
            customer_id TEXT,
            order_date TEXT NOT NULL,
            status TEXT NOT NULL,
            region_code TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        );
    """)

    cursor.execute("""
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

    # 1. Load customers
    with open(cleaned_dir / "customers_cleaned.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        cust_rows = [(r["customer_id"], r["customer_name"], r["email"], r["registration_date"], r["customer_type"]) for r in reader]
        cursor.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?);", cust_rows)

    # 2. Load products
    with open(cleaned_dir / "products_cleaned.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        prod_rows = [(r["product_id"], r["product_name"], r["category"], r["subcategory"], float(r["cost_price"])) for r in reader]
        cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?);", prod_rows)

    # 3. Load orders (Map empty string customer_id to None/NULL)
    with open(cleaned_dir / "orders_cleaned.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        order_rows = []
        for r in reader:
            cid = r["customer_id"].strip() if r["customer_id"] and r["customer_id"].strip() else None
            order_rows.append((r["order_id"], cid, r["order_date"], r["status"], r["region_code"]))
        cursor.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?);", order_rows)

    # 4. Load order items
    with open(cleaned_dir / "order_items_cleaned.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        item_rows = [
            (
                r["item_id"],
                r["order_id"],
                r["product_id"],
                int(r["quantity"]),
                float(r["unit_price"]),
                float(r["discount_percent"])
            )
            for r in reader
        ]
        cursor.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?, ?, ?);", item_rows)

    conn.commit()

    # Integrity & FK checks
    cursor.execute("PRAGMA integrity_check;")
    integrity = cursor.fetchone()[0]

    cursor.execute("PRAGMA foreign_key_check;")
    fk_violations = cursor.fetchall()

    print(f"[Database Load] SQLite database created at {db_path}")
    print(f"  Customers loaded: {len(cust_rows)}")
    print(f"  Products loaded: {len(prod_rows)}")
    print(f"  Orders loaded: {len(order_rows)}")
    print(f"  Order Items loaded: {len(item_rows)}")
    print(f"  PRAGMA integrity_check: {integrity}")
    print(f"  PRAGMA foreign_key_check: {len(fk_violations)} violations")

    conn.close()
    return integrity == "ok" and len(fk_violations) == 0


if __name__ == "__main__":
    load_database()
