"""
Data Generation Script for E-Commerce Order Analytics System
Generates synthetic raw CSV files with intentional real-world anomalies:
- Missing customer IDs (~5%)
- Negative item quantities (~3% returns)
- Malformed order dates (DD-MM-YYYY format)
- Corrupted product names (leading/trailing whitespace, mixed casing)
- Invalid customer email addresses (~2%)
- Orphan order items (referential integrity defects)
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path


def generate_raw_data(seed: int = 42, base_dir: Path = None):
    random.seed(seed)
    if base_dir is None:
        base_dir = Path(__file__).resolve().parent.parent.parent
    
    raw_dir = base_dir / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    # 1. Generate Customers (1,000)
    customer_types = ["REGULAR", "PREMIUM", "VIP"]
    first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]
    domains = ["gmail.com", "yahoo.com", "outlook.com", "example.com", "store.net"]

    customers = []
    num_customers = 1000
    invalid_email_indices = set(random.sample(range(num_customers), int(num_customers * 0.02)))  # 2% invalid

    start_reg_date = datetime(2022, 1, 1)
    
    for i in range(num_customers):
        cid = f"CUST-{i+1:05d}"
        fname = random.choice(first_names)
        lname = random.choice(last_names)
        cname = f"{fname} {lname}"
        
        if i in invalid_email_indices:
            # Generate malformed email
            malformed_choice = random.choice([
                f"{fname.lower()}{lname.lower()}atgmail.com",
                f"{fname.lower()}.{lname.lower()}@domain_without_extension",
                f"{fname.lower()}{lname.lower()}#example.com",
                f"invalid_email_{i+1}"
            ])
            email = malformed_choice
        else:
            email = f"{fname.lower()}.{lname.lower()}{i+1}@{random.choice(domains)}"
            
        reg_date = start_reg_date + timedelta(days=random.randint(0, 700))
        reg_str = reg_date.strftime("%Y-%m-%d %H:%M:%S")
        ctype = random.choices(customer_types, weights=[0.7, 0.2, 0.1])[0]
        
        customers.append({
            "customer_id": cid,
            "customer_name": cname,
            "email": email,
            "registration_date": reg_str,
            "customer_type": ctype
        })

    customers_csv = raw_dir / "customers.csv"
    with open(customers_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["customer_id", "customer_name", "email", "registration_date", "customer_type"])
        writer.writeheader()
        writer.writerows(customers)

    # 2. Generate Products (500)
    categories = {
        "Electronics": ["Headphones", "Smartphones", "Laptops", "Monitors", "Keyboards", "Cameras", "Tablets", "Smartwatches"],
        "Clothing": ["T-Shirts", "Jeans", "Jackets", "Hoodies", "Sneakers", "Dresses", "Socks", "Sweaters"],
        "Home": ["Coffee Maker", "Blender", "Vacuum Cleaner", "Desk Lamp", "Air Purifier", "Bed Sheets", "Cookware Set"],
        "Books": ["Fiction Novel", "Tech Guide", "Cookbook", "History Anthology", "Biography", "Science Journal"]
    }

    products = []
    num_products = 500
    corrupt_product_indices = set(random.sample(range(num_products), int(num_products * 0.06)))

    for i in range(num_products):
        pid = f"PROD-{i+1:04d}"
        cat = random.choice(list(categories.keys()))
        subcat = random.choice(categories[cat])
        base_name = f"{subcat} Model-{random.randint(100, 999)}"
        cost_price = round(random.uniform(5.0, 500.0), 2)

        if i in corrupt_product_indices:
            # Corrupt whitespace / casing
            if i % 2 == 0:
                pname = f"   {base_name.lower()}   "
            else:
                pname = f"{base_name.swapcase()}"
        else:
            pname = base_name

        products.append({
            "product_id": pid,
            "product_name": pname,
            "category": cat,
            "subcategory": subcat,
            "cost_price": cost_price
        })

    products_csv = raw_dir / "products.csv"
    with open(products_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["product_id", "product_name", "category", "subcategory", "cost_price"])
        writer.writeheader()
        writer.writerows(products)

    # 3. Generate Orders (1,000)
    statuses = ["PLACED", "SHIPPED", "DELIVERED", "CANCELLED", "RETURNED"]
    status_weights = [0.15, 0.15, 0.55, 0.08, 0.07]
    regions = ["US-EAST", "US-WEST", "EU-CENTRAL", "APAC-EAST", "LATAM-SOUTH"]

    orders = []
    num_orders = 1000
    missing_cust_indices = set(random.sample(range(num_orders), int(num_orders * 0.05)))  # 5% missing customer_id
    bad_date_indices = set(random.sample(range(num_orders), int(num_orders * 0.05)))       # 5% DD-MM-YYYY format

    start_order_date = datetime(2023, 1, 1)
    
    for i in range(num_orders):
        oid = f"ORD-{i+1:06d}"
        
        if i in missing_cust_indices:
            cid = ""  # Guest checkout (NULL)
        else:
            cid = random.choice(customers)["customer_id"]
            
        dt = start_order_date + timedelta(days=random.randint(0, 550), hours=random.randint(0, 23), minutes=random.randint(0, 59))
        
        if i in bad_date_indices:
            date_str = dt.strftime("%d-%m-%Y")
        else:
            date_str = dt.strftime("%Y-%m-%d %H:%M:%S")

        status = random.choices(statuses, weights=status_weights)[0]
        region = random.choice(regions)

        orders.append({
            "order_id": oid,
            "customer_id": cid,
            "order_date": date_str,
            "status": status,
            "region_code": region
        })

    orders_csv = raw_dir / "orders.csv"
    with open(orders_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["order_id", "customer_id", "order_date", "status", "region_code"])
        writer.writeheader()
        writer.writerows(orders)

    # 4. Generate Order Items (2,000)
    order_items = []
    num_items = 2000
    neg_qty_indices = set(random.sample(range(num_items), int(num_items * 0.03)))  # 3% negative quantity
    orphan_item_indices = set(random.sample(range(num_items), 30))                 # 30 orphan items

    for i in range(num_items):
        item_id = f"ITEM-{i+1:06d}"
        
        if i in orphan_item_indices:
            # References non-existent order
            oid = f"ORD-999{random.randint(100, 999):03d}"
        else:
            oid = random.choice(orders)["order_id"]
            
        prod = random.choice(products)
        pid = prod["product_id"]
        
        # Unit price derived from cost price with markup
        unit_price = round(prod["cost_price"] * random.uniform(1.2, 1.8), 2)
        discount = round(random.choice([0.0, 0.0, 0.0, 5.0, 10.0, 15.0, 20.0]), 2)
        
        if i in neg_qty_indices:
            qty = -random.randint(1, 3)
        else:
            qty = random.randint(1, 5)

        order_items.append({
            "item_id": item_id,
            "order_id": oid,
            "product_id": pid,
            "quantity": qty,
            "unit_price": unit_price,
            "discount_percent": discount
        })

    order_items_csv = raw_dir / "order_items.csv"
    with open(order_items_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["item_id", "order_id", "product_id", "quantity", "unit_price", "discount_percent"])
        writer.writeheader()
        writer.writerows(order_items)

    print(f"[Data Generation] Success!")
    print(f"  Customers: {len(customers)} -> {customers_csv}")
    print(f"  Products: {len(products)} -> {products_csv}")
    print(f"  Orders: {len(orders)} -> {orders_csv}")
    print(f"  Order Items: {len(order_items)} -> {order_items_csv}")


if __name__ == "__main__":
    generate_raw_data()
