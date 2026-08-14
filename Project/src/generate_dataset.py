#!/usr/bin/env python3
"""
Dataset Generator & Validator for Databricks Late Transaction Project.
Generates Project_Dataset.csv conforming to authoritative specifications:
- Exactly 2,000 transactions
- 400 unique users
- 60 unique transaction dates (2024-01-01 through 2024-02-29)
- Ingestion dates through 2024-03-14
- Exactly 1,415 late-arriving transactions (ingestion_date > txn_date)
- Exactly 585 on-time transactions (ingestion_date == txn_date)
- Zero duplicates, nulls, negative or zero amounts
"""

import csv
import datetime
import random
from pathlib import Path

def generate_dataset(output_path: str = "data/Project_Dataset.csv") -> dict:
    random.seed(42)  # Deterministic seed

    # 60 transaction dates: 2024-01-01 to 2024-02-29 (2024 is leap year: 31 Jan + 29 Feb = 60 days)
    start_txn_date = datetime.date(2024, 1, 1)
    end_txn_date = datetime.date(2024, 2, 29)
    txn_dates = []
    curr = start_txn_date
    while curr <= end_txn_date:
        txn_dates.append(curr)
        curr += datetime.timedelta(days=1)
    
    assert len(txn_dates) == 60, f"Expected 60 dates, got {len(txn_dates)}"

    # Ingestion cutoff: 2024-03-14
    max_ingestion_date = datetime.date(2024, 3, 14)

    # 400 unique users
    users = list(range(1001, 1401))
    assert len(users) == 400

    total_records = 2000
    target_late = 1415
    target_ontime = 585

    # Assign transaction dates ensuring all 60 dates have at least some transactions
    assigned_txn_dates = []
    # Guarantee at least 20 transactions per date initially (60 * 20 = 1200)
    for d in txn_dates:
        assigned_txn_dates.extend([d] * 20)
    # Distribute remaining 800 across the 60 dates
    for _ in range(total_records - len(assigned_txn_dates)):
        assigned_txn_dates.append(random.choice(txn_dates))
    
    random.shuffle(assigned_txn_dates)

    # Decide which indices are on-time (585) and which are late (1415)
    indices = list(range(total_records))
    random.shuffle(indices)
    ontime_indices = set(indices[:target_ontime])
    late_indices = set(indices[target_ontime:])

    # Track user distribution so all 400 users are represented
    assigned_users = users.copy()
    # Fill remaining 1600 user slots
    for _ in range(total_records - len(users)):
        assigned_users.append(random.choice(users))
    random.shuffle(assigned_users)

    records = []
    for i in range(total_records):
        txn_id = 100001 + i
        user_id = assigned_users[i]
        txn_date = assigned_txn_dates[i]

        # Generate realistic amount (e.g., $10.50 to $950.00)
        amount = round(random.uniform(10.0, 950.0), 2)
        assert amount > 0

        if i in ontime_indices:
            ingestion_date = txn_date
        else:
            # Late transaction: ingestion_date > txn_date and <= 2024-03-14
            min_late_date = txn_date + datetime.timedelta(days=1)
            days_diff = (max_ingestion_date - min_late_date).days
            if days_diff > 0:
                lag = random.randint(1, min(days_diff, 20)) # 1 to 20 days lag
                ingestion_date = min_late_date + datetime.timedelta(days=lag - 1)
                if ingestion_date > max_ingestion_date:
                    ingestion_date = max_ingestion_date
            else:
                ingestion_date = max_ingestion_date
            
            assert ingestion_date > txn_date, f"Late transaction error: {ingestion_date} <= {txn_date}"

        records.append({
            "txn_id": txn_id,
            "user_id": user_id,
            "txn_date": txn_date.strftime("%Y-%m-%d"),
            "amount": f"{amount:.2f}",
            "ingestion_date": ingestion_date.strftime("%Y-%m-%d")
        })

    # Write to CSV
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["txn_id", "user_id", "txn_date", "amount", "ingestion_date"])
        writer.writeheader()
        writer.writerows(records)

    # Verification stats
    stats = verify_dataset(output_path)
    return stats

def verify_dataset(file_path: str = "data/Project_Dataset.csv") -> dict:
    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    
    total = len(reader)
    txn_ids = set()
    user_ids = set()
    txn_dates = set()
    ingestion_dates = set()
    late_count = 0
    ontime_count = 0
    null_count = 0
    invalid_amount_count = 0

    for r in reader:
        # Check nulls
        if any(v is None or v == "" for v in r.values()):
            null_count += 1
        
        txn_ids.add(r["txn_id"])
        user_ids.add(r["user_id"])
        
        t_date = datetime.datetime.strptime(r["txn_date"], "%Y-%m-%d").date()
        i_date = datetime.datetime.strptime(r["ingestion_date"], "%Y-%m-%d").date()
        
        txn_dates.add(t_date)
        ingestion_dates.add(i_date)

        amt = float(r["amount"])
        if amt <= 0:
            invalid_amount_count += 1

        if i_date > t_date:
            late_count += 1
        elif i_date == t_date:
            ontime_count += 1

    stats = {
        "total_records": total,
        "unique_txn_ids": len(txn_ids),
        "unique_users": len(user_ids),
        "unique_txn_dates": len(txn_dates),
        "min_txn_date": min(txn_dates).strftime("%Y-%m-%d"),
        "max_txn_date": max(txn_dates).strftime("%Y-%m-%d"),
        "min_ingestion_date": min(ingestion_dates).strftime("%Y-%m-%d"),
        "max_ingestion_date": max(ingestion_dates).strftime("%Y-%m-%d"),
        "late_transactions": late_count,
        "ontime_transactions": ontime_count,
        "null_count": null_count,
        "invalid_amount_count": invalid_amount_count
    }
    return stats

if __name__ == "__main__":
    stats = generate_dataset()
    print("=== Dataset Generation & Verification Summary ===")
    for k, v in stats.items():
        print(f"  {k}: {v}")
