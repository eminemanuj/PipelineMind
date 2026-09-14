"""
scripts/generate_mock_data.py — Mock Data Generator
--------------------------------------------------------
Generates realistic-looking (but fake) customer and order data using
Faker, and loads it into a real DuckDB database file.

Run this once to set up the warehouse:
    python scripts/generate_mock_data.py
"""

import duckdb
from faker import Faker
import random

fake = Faker()
Faker.seed(42)
random.seed(42)

DB_PATH = "data/raw/warehouse.duckdb"
NUM_CUSTOMERS = 500
NUM_ORDERS = 2000


def generate_customers(n: int) -> list[dict]:
    customers = []
    for i in range(n):
        customers.append({
            "customer_id": i + 1,
            "full_name": fake.name(),
            "email": fake.email(),
            "signup_date": fake.date_between(start_date="-3y", end_date="today"),
            "city": fake.city(),
            "country": fake.country(),
        })
    return customers


def generate_orders(n: int, num_customers: int) -> list[dict]:
    orders = []
    for i in range(n):
        order_date = fake.date_time_between(start_date="-2y", end_date="now")
        orders.append({
            "order_id": i + 1,
            "customer_id": random.randint(1, num_customers),
            "order_amount": round(random.uniform(10.0, 500.0), 2),
            "order_status": random.choices(
                ["completed", "pending", "cancelled"], weights=[0.85, 0.1, 0.05]
            )[0],
            "order_timestamp": order_date,
        })
    return orders


def load_into_duckdb(customers: list[dict], orders: list[dict]):
    conn = duckdb.connect(DB_PATH)

    conn.execute("""
        CREATE OR REPLACE TABLE raw_customers (
            customer_id INTEGER,
            full_name VARCHAR,
            email VARCHAR,
            signup_date DATE,
            city VARCHAR,
            country VARCHAR
        )
    """)
    conn.executemany(
        "INSERT INTO raw_customers VALUES (?, ?, ?, ?, ?, ?)",
        [(c["customer_id"], c["full_name"], c["email"], c["signup_date"], c["city"], c["country"]) for c in customers],
    )

    conn.execute("""
        CREATE OR REPLACE TABLE raw_orders (
            order_id INTEGER,
            customer_id INTEGER,
            order_amount DOUBLE,
            order_status VARCHAR,
            order_timestamp TIMESTAMP
        )
    """)
    conn.executemany(
        "INSERT INTO raw_orders VALUES (?, ?, ?, ?, ?)",
        [(o["order_id"], o["customer_id"], o["order_amount"], o["order_status"], o["order_timestamp"]) for o in orders],
    )

    conn.close()


if __name__ == "__main__":
    print("Generating mock customers...")
    customers = generate_customers(NUM_CUSTOMERS)
    print("Generating mock orders...")
    orders = generate_orders(NUM_ORDERS, NUM_CUSTOMERS)

    print(f"Loading into DuckDB at {DB_PATH}...")
    load_into_duckdb(customers, orders)

    conn = duckdb.connect(DB_PATH)
    print("\n=== Verification ===")
    print("raw_customers:", conn.execute("SELECT COUNT(*) FROM raw_customers").fetchone()[0], "rows")
    print("raw_orders:", conn.execute("SELECT COUNT(*) FROM raw_orders").fetchone()[0], "rows")
    conn.close()