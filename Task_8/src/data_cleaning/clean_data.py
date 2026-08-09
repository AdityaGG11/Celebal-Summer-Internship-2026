"""
Data Cleaning and Validation Module for E-Commerce Order Analytics System
Provides clean_orders(), clean_products(), validate_emails(), and check_referential_integrity().
Outputs cleaned CSVs and a concise data_quality_report.md.
"""

import re
from datetime import datetime
from pathlib import Path
import pandas as pd


def clean_orders(orders_df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """
    Cleans orders dataframe:
    - Normalizes DD-MM-YYYY dates to YYYY-MM-DD 00:00:00
    - Preserves missing customer_id (guest checkouts)
    """
    df = orders_df.copy()
    malformed_count = 0

    def parse_and_format_date(date_str: str) -> str:
        nonlocal malformed_count
        if not isinstance(date_str, str) or not date_str.strip():
            return date_str
        
        date_str = date_str.strip()
        # Check DD-MM-YYYY
        if re.match(r"^\d{2}-\d{2}-\d{4}$", date_str):
            malformed_count += 1
            dt = datetime.strptime(date_str, "%d-%m-%Y")
            return dt.strftime("%Y-%m-%d 00:00:00")
        
        # Check standard format YYYY-MM-DD HH:MM:SS or YYYY-MM-DD
        try:
            if len(date_str) == 10:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                return dt.strftime("%Y-%m-%d 00:00:00")
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            return date_str

    df["order_date"] = df["order_date"].apply(parse_and_format_date)
    # Ensure empty string / NaN customer_id is explicitly represented as empty string or NaN
    df["customer_id"] = df["customer_id"].fillna("").astype(str).str.strip()
    return df, malformed_count


def clean_products(products_df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """
    Cleans products dataframe:
    - Trims whitespace
    - Normalizes product names to title case
    """
    df = products_df.copy()
    normalized_count = 0

    def normalize_name(name_str: str) -> str:
        nonlocal normalized_count
        if not isinstance(name_str, str):
            return name_str
        stripped = name_str.strip()
        titled = stripped.title()
        if name_str != titled:
            normalized_count += 1
        return titled

    df["product_name"] = df["product_name"].apply(normalize_name)
    return df, normalized_count


def validate_emails(customers_df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    """
    Validates customer emails using regex pattern.
    Returns customer dataframe and list of invalid email records.
    Does NOT delete invalid customer records.
    """
    df = customers_df.copy()
    email_regex = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    invalid_records = []

    for idx, row in df.iterrows():
        email = str(row["email"]).strip() if pd.notna(row["email"]) else ""
        if not email_regex.match(email):
            invalid_records.append({
                "customer_id": row["customer_id"],
                "customer_name": row["customer_name"],
                "invalid_email": email
            })

    return df, invalid_records


def check_referential_integrity(order_items_df: pd.DataFrame, orders_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Identifies order_items whose order_id does not exist in orders.
    Returns (cleaned_order_items_df, orphan_order_items_df).
    """
    valid_order_ids = set(orders_df["order_id"].dropna().astype(str).str.strip())
    
    is_orphan = ~order_items_df["order_id"].astype(str).str.strip().isin(valid_order_ids)
    
    orphan_df = order_items_df[is_orphan].copy()
    cleaned_df = order_items_df[~is_orphan].copy()
    
    return cleaned_df, orphan_df


def run_cleaning_pipeline(base_dir: Path = None):
    if base_dir is None:
        base_dir = Path(__file__).resolve().parent.parent.parent

    raw_dir = base_dir / "data" / "raw"
    cleaned_dir = base_dir / "data" / "cleaned"
    cleaned_dir.mkdir(parents=True, exist_ok=True)

    # Load raw CSVs
    orders_raw = pd.read_csv(raw_dir / "orders.csv", dtype=str)
    products_raw = pd.read_csv(raw_dir / "products.csv")
    customers_raw = pd.read_csv(raw_dir / "customers.csv", dtype=str)
    order_items_raw = pd.read_csv(raw_dir / "order_items.csv")

    # Clean orders
    orders_cleaned, malformed_dates_cnt = clean_orders(orders_raw)
    missing_cust_cnt = int((orders_cleaned["customer_id"] == "").sum())

    # Clean products
    products_cleaned, normalized_products_cnt = clean_products(products_raw)

    # Validate emails
    customers_cleaned, invalid_emails = validate_emails(customers_raw)

    # Referential integrity check
    order_items_cleaned, orphan_order_items = check_referential_integrity(order_items_raw, orders_cleaned)
    neg_qty_cnt = int((order_items_cleaned["quantity"] < 0).sum())

    # Save cleaned files
    orders_cleaned.to_csv(cleaned_dir / "orders_cleaned.csv", index=False)
    products_cleaned.to_csv(cleaned_dir / "products_cleaned.csv", index=False)
    customers_cleaned.to_csv(cleaned_dir / "customers_cleaned.csv", index=False)
    order_items_cleaned.to_csv(cleaned_dir / "order_items_cleaned.csv", index=False)
    orphan_order_items.to_csv(cleaned_dir / "orphan_order_items.csv", index=False)

    # Generate Data Quality Report
    report_content = f"""# Data Quality & Cleaning Summary Report

## Pipeline Execution Summary
- **Source Files**: `data/raw/` (orders, products, customers, order_items)
- **Target Files**: `data/cleaned/`

## Key Cleaning Metrics
1. **Orders Data**:
   - Total Orders Processed: {len(orders_cleaned)}
   - Malformed Dates (`DD-MM-YYYY`) Corrected: {malformed_dates_cnt}
   - Guest Checkout Orders (Missing `customer_id` Preserved): {missing_cust_cnt}

2. **Products Data**:
   - Total Products Processed: {len(products_cleaned)}
   - Product Names Trimmed & Normalized to Title Case: {normalized_products_cnt}

3. **Customers Data**:
   - Total Customers Processed: {len(customers_cleaned)}
   - Invalid Email Addresses Detected & Flagged: {len(invalid_emails)}
   *(Note: Invalid customers are preserved for analysis without silent deletion)*

4. **Order Items Data**:
   - Total Raw Items: {len(order_items_raw)}
   - Valid Items Saved to `order_items_cleaned.csv`: {len(order_items_cleaned)}
   - Orphan Items Isolated to `orphan_order_items.csv`: {len(orphan_order_items)}
   - Return Transactions (Negative Quantities Preserved): {neg_qty_cnt}

## Integrity & Quality Safeguards
- Raw source files preserved intact.
- Business semantics maintained (guest checkouts, negative return quantities, and invalid emails retained).
- Referential integrity defects explicitly segregated to `orphan_order_items.csv`.
"""

    report_path = cleaned_dir / "data_quality_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    print("[Data Cleaning] Pipeline Complete!")
    print(f"  Orders Cleaned: {len(orders_cleaned)} (Malformed dates fixed: {malformed_dates_cnt})")
    print(f"  Products Cleaned: {len(products_cleaned)} (Normalized: {normalized_products_cnt})")
    print(f"  Customers Validated: {len(customers_cleaned)} (Invalid emails: {len(invalid_emails)})")
    print(f"  Order Items Cleaned: {len(order_items_cleaned)} (Orphans isolated: {len(orphan_order_items)})")
    print(f"  Quality Report: {report_path}")


if __name__ == "__main__":
    run_cleaning_pipeline()
