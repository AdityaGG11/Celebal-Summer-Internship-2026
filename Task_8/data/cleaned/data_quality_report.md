# Data Quality & Cleaning Summary Report

## Pipeline Execution Summary
- **Source Files**: `data/raw/` (orders, products, customers, order_items)
- **Target Files**: `data/cleaned/`

## Key Cleaning Metrics
1. **Orders Data**:
   - Total Orders Processed: 1000
   - Malformed Dates (`DD-MM-YYYY`) Corrected: 50
   - Guest Checkout Orders (Missing `customer_id` Preserved): 50

2. **Products Data**:
   - Total Products Processed: 500
   - Product Names Trimmed & Normalized to Title Case: 30

3. **Customers Data**:
   - Total Customers Processed: 1000
   - Invalid Email Addresses Detected & Flagged: 20
   *(Note: Invalid customers are preserved for analysis without silent deletion)*

4. **Order Items Data**:
   - Total Raw Items: 2000
   - Valid Items Saved to `order_items_cleaned.csv`: 1970
   - Orphan Items Isolated to `orphan_order_items.csv`: 30
   - Return Transactions (Negative Quantities Preserved): 59

## Integrity & Quality Safeguards
- Raw source files preserved intact.
- Business semantics maintained (guest checkouts, negative return quantities, and invalid emails retained).
- Referential integrity defects explicitly segregated to `orphan_order_items.csv`.
