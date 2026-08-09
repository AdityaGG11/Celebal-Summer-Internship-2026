"""
CLI Reporting Module for E-Commerce Order Analytics System
Strictly uses sqlite3 and Python standard library only (no external dependencies).

Features:
- Report Types: Daily, Weekly, Monthly
- Custom Date Range input with validation
- Summary Metrics: Total Orders, Revenue, Unique Customers (excluding guest checkouts), Top 3 Products
- Period-over-Period Percentage Comparison with safe zero-baseline handling
- Interactive CLI prompt + optional argument-driven non-interactive mode for automated testing.
"""

import sys
import sqlite3
import argparse
from datetime import datetime, timedelta
from pathlib import Path


def get_db_connection(base_dir: Path = None) -> sqlite3.Connection:
    if base_dir is None:
        base_dir = Path(__file__).resolve().parent.parent.parent
    db_path = base_dir / "database" / "ecommerce.db"
    if not db_path.exists():
        raise FileNotFoundError(f"Database file not found at {db_path}. Please run load_database.py first.")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def calculate_pct_change(current: float, previous: float) -> str:
    """
    Calculates percentage change safely.
    Returns string 'N/A' if previous baseline is 0 or undefined.
    """
    if previous is None or previous == 0:
        return "N/A"
    pct = ((current - previous) / previous) * 100.0
    return f"{pct:+.2f}%"


def parse_date(date_str: str) -> datetime:
    """Parses date string YYYY-MM-DD into datetime object."""
    date_str = date_str.strip()
    return datetime.strptime(date_str, "%Y-%m-%d")


def fetch_period_metrics(conn: sqlite3.Connection, start_str: str, end_str: str) -> dict:
    """
    Fetches total orders, revenue, unique customers (excluding NULL customer_id),
    and top 3 products for the inclusive date range [start_str 00:00:00, end_str 23:59:59].
    """
    start_dt = f"{start_str} 00:00:00"
    end_dt = f"{end_str} 23:59:59"

    cursor = conn.cursor()

    # 1. Total Orders, Revenue, Unique Customers
    query_summary = """
        SELECT 
            COUNT(DISTINCT o.order_id) AS total_orders,
            COALESCE(SUM(oi.quantity * oi.unit_price * (1.0 - oi.discount_percent / 100.0)), 0.0) AS total_revenue,
            COUNT(DISTINCT o.customer_id) AS unique_customers
        FROM orders o
        LEFT JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.status != 'CANCELLED'
          AND o.order_date >= ? AND o.order_date <= ?;
    """
    cursor.execute(query_summary, (start_dt, end_dt))
    row = cursor.fetchone()

    total_orders = row["total_orders"] if row else 0
    total_revenue = round(row["total_revenue"], 2) if row and row["total_revenue"] else 0.0
    unique_customers = row["unique_customers"] if row else 0

    # 2. Top 3 Products
    query_top_products = """
        SELECT 
            p.product_name,
            p.category,
            SUM(CASE WHEN oi.quantity > 0 THEN oi.quantity ELSE 0 END) AS units_sold,
            ROUND(SUM(oi.quantity * oi.unit_price * (1.0 - oi.discount_percent / 100.0)), 2) AS product_revenue
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        JOIN orders o ON oi.order_id = o.order_id
        WHERE o.status != 'CANCELLED'
          AND o.order_date >= ? AND o.order_date <= ?
        GROUP BY p.product_id, p.product_name, p.category
        ORDER BY product_revenue DESC
        LIMIT 3;
    """
    cursor.execute(query_top_products, (start_dt, end_dt))
    top_products = [dict(r) for r in cursor.fetchall()]

    return {
        "total_orders": total_orders,
        "revenue": total_revenue,
        "unique_customers": unique_customers,
        "top_products": top_products
    }


def generate_report(report_type: str, start_date_str: str, end_date_str: str, conn: sqlite3.Connection = None) -> str:
    """
    Generates a text summary report for specified report_type and date range.
    Calculates previous period comparison metrics automatically based on period duration.
    """
    try:
        start_dt = parse_date(start_date_str)
        end_dt = parse_date(end_date_str)
    except ValueError:
        return f"Error: Invalid date format. Please use YYYY-MM-DD format. Received start='{start_date_str}', end='{end_date_str}'."

    if start_dt > end_dt:
        return f"Error: Start date ({start_date_str}) cannot be after end date ({end_date_str})."

    # Calculate duration (number of days)
    duration_days = (end_dt - start_dt).days + 1

    # Calculate previous period start and end dates
    prev_end_dt = start_dt - timedelta(days=1)
    prev_start_dt = prev_end_dt - timedelta(days=duration_days - 1)

    prev_start_str = prev_start_dt.strftime("%Y-%m-%d")
    prev_end_str = prev_end_dt.strftime("%Y-%m-%d")

    close_conn_on_exit = False
    if conn is None:
        conn = get_db_connection()
        close_conn_on_exit = True

    current_metrics = fetch_period_metrics(conn, start_date_str, end_date_str)
    previous_metrics = fetch_period_metrics(conn, prev_start_str, prev_end_str)

    if close_conn_on_exit:
        conn.close()

    # Calculate % changes
    orders_pct = calculate_pct_change(current_metrics["total_orders"], previous_metrics["total_orders"])
    revenue_pct = calculate_pct_change(current_metrics["revenue"], previous_metrics["revenue"])
    cust_pct = calculate_pct_change(current_metrics["unique_customers"], previous_metrics["unique_customers"])

    # Build Output
    divider = "=" * 65
    sub_divider = "-" * 65

    output_lines = [
        divider,
        f"        E-COMMERCE ANALYTICS {report_type.upper()} SUMMARY REPORT",
        divider,
        f" Selected Period:   {start_date_str} to {end_date_str} ({duration_days} days)",
        f" Comparison Period: {prev_start_str} to {prev_end_str} ({duration_days} days)",
        sub_divider,
        " KEY METRICS & PERIOD-OVER-PERIOD COMPARISON:",
        f"  • Total Orders:      {current_metrics['total_orders']:<10} (Prev: {previous_metrics['total_orders']:<8} | Change: {orders_pct})",
        f"  • Total Revenue:     ${current_metrics['revenue']:<9.2f} (Prev: ${previous_metrics['revenue']:<7.2f} | Change: {revenue_pct})",
        f"  • Unique Customers:  {current_metrics['unique_customers']:<10} (Prev: {previous_metrics['unique_customers']:<8} | Change: {cust_pct})",
        "    *(Note: Guest checkouts without Customer ID are excluded from customer count)*",
        sub_divider,
        " TOP 3 PERFORMING PRODUCTS IN PERIOD:"
    ]

    if current_metrics["top_products"]:
        for idx, prod in enumerate(current_metrics["top_products"], start=1):
            pname = prod["product_name"]
            cat = prod["category"]
            rev = prod["product_revenue"]
            units = prod["units_sold"]
            output_lines.append(f"  {idx}. {pname} [{cat}]")
            output_lines.append(f"     Revenue: ${rev:,.2f} | Units Sold: {units}")
    else:
        output_lines.append("  No sales recorded during this period.")

    output_lines.append(divider)
    return "\n".join(output_lines)


def interactive_cli():
    print("=========================================================")
    print("       E-Commerce Order Analytics System CLI Report      ")
    print("=========================================================")
    print("Select Report Type:")
    print("  1. Daily")
    print("  2. Weekly")
    print("  3. Monthly")

    try:
        type_choice = input("Enter choice (1-3) [default: 1]: ").strip()
    except EOFError:
        type_choice = "1"

    type_map = {"1": "Daily", "2": "Weekly", "3": "Monthly"}
    report_type = type_map.get(type_choice, "Daily")

    print(f"\nReport Mode selected: {report_type}")
    
    default_start = "2023-01-01"
    default_end = "2023-01-31"

    try:
        start_input = input(f"Enter Start Date (YYYY-MM-DD) [default: {default_start}]: ").strip()
    except EOFError:
        start_input = default_start
    start_date = start_input if start_input else default_start

    try:
        end_input = input(f"Enter End Date (YYYY-MM-DD) [default: {default_end}]: ").strip()
    except EOFError:
        end_input = default_end
    end_date = end_input if end_input else default_end

    print("\nGenerating report...\n")
    report_text = generate_report(report_type, start_date, end_date)
    print(report_text)


def main():
    parser = argparse.ArgumentParser(description="E-Commerce Order Analytics CLI Reporting Tool")
    parser.add_argument("--type", choices=["daily", "weekly", "monthly", "Daily", "Weekly", "Monthly"], help="Report type")
    parser.add_argument("--start", help="Start date in YYYY-MM-DD format")
    parser.add_argument("--end", help="End date in YYYY-MM-DD format")

    args = parser.parse_args()

    if args.type and args.start and args.end:
        # Non-interactive mode
        report_text = generate_report(args.type, args.start, args.end)
        print(report_text)
    else:
        # Interactive mode
        interactive_cli()


if __name__ == "__main__":
    main()
