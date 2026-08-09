"""
SQL Analytics Runner Module
Executes all 17 SQL files in sql/ against database/ecommerce.db and displays results summary.
"""

import sqlite3
from pathlib import Path


def run_all_queries(base_dir: Path = None):
    if base_dir is None:
        base_dir = Path(__file__).resolve().parent.parent.parent

    db_path = base_dir / "database" / "ecommerce.db"
    sql_dir = base_dir / "sql"

    if not db_path.exists():
        raise FileNotFoundError(f"Database not found at {db_path}. Please run load_database.py first.")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    sql_files = sorted(list(sql_dir.glob("*.sql")))
    print(f"[SQL Runner] Found {len(sql_files)} SQL query files in {sql_dir}\n")

    results_summary = []

    for sql_file in sql_files:
        filename = sql_file.name
        with open(sql_file, "r", encoding="utf-8") as f:
            sql_script = f.read().strip()

        try:
            cursor.execute(sql_script)
            rows = cursor.fetchall()
            col_names = [desc[0] for desc in cursor.description] if cursor.description else []
            row_count = len(rows)
            
            print(f"✅ Executed {filename} successfully ({row_count} rows returned)")
            if row_count > 0 and col_names:
                # Print preview of top 2 rows
                print(f"   Columns: {', '.join(col_names)}")
                for r in rows[:2]:
                    print(f"   Row: {r}")
            print("-" * 60)
            
            results_summary.append({
                "file": filename,
                "status": "SUCCESS",
                "rows": row_count
            })

        except Exception as e:
            print(f"❌ Failed executing {filename}: {e}")
            print("-" * 60)
            results_summary.append({
                "file": filename,
                "status": f"FAILED: {e}",
                "rows": 0
            })

    conn.close()

    success_cnt = sum(1 for r in results_summary if r["status"] == "SUCCESS")
    print(f"\n[SQL Runner Execution Complete]: {success_cnt}/{len(sql_files)} queries passed.")
    return results_summary


if __name__ == "__main__":
    run_all_queries()
