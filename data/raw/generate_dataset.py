"""
generate_dataset.py
-------------------
Generates three synthetic CSV files that simulate a small e-commerce business.
Run once before ingesting into DuckDB.

Output:
    data/raw/orders_raw.csv
    data/raw/customers_raw.csv
    data/raw/products_raw.csv

Intentional data quality issues injected into orders_raw.csv only:
    - Some order_date values use MM/DD/YYYY instead of YYYY-MM-DD
    - ~3% of orders have NULL customer_id
    - ~2% of order rows are duplicates
    - Some quantity values are 0 or negative (invalid)

customers_raw.csv and products_raw.csv are clean by design.
"""

import csv
import os
import random
from datetime import date, timedelta

# ── Reproducibility ───────────────────────────────────────────────────────────
random.seed(42)

# ── Output paths ─────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_ORDERS = os.path.join(BASE_DIR, "orders_raw.csv")
OUT_CUSTOMERS = os.path.join(BASE_DIR, "customers_raw.csv")
OUT_PRODUCTS = os.path.join(BASE_DIR, "products_raw.csv")

# ── Reference data ────────────────────────────────────────────────────────────
COUNTRIES = ["US", "DE", "FR", "GB", "ES", "MX", "BR", "CA", "AU", "JP"]
SEGMENTS = ["consumer", "corporate", "small_business"]
STATUSES = ["completed", "completed", "completed", "returned", "cancelled"]  # weighted
CATEGORIES = [
    "Electronics",
    "Clothing",
    "Home & Garden",
    "Sports",
    "Books",
]
BRANDS = [
    "TechNova",
    "StyleCo",
    "HomeBase",
    "ActiveGear",
    "PageTurner",
    "GenericBrand",
    "PremiumLine",
    "ApexWear",
    "NovaTech",
    "UrbanEdge",
]

# Real product names per normalized category
PRODUCTS_BY_CATEGORY = {
    "Electronics": [
        "Laptop Computer 15-inch",
        "Wireless Bluetooth Headphones",
        "4K Smart TV 55-inch",
        "USB-C Charging Hub",
        "Mechanical Keyboard",
        "Noise Cancelling Earbuds",
        "Portable Bluetooth Speaker",
        "Gaming Mouse",
        "Webcam 1080p",
        "External SSD 1TB",
        "Tablet 10-inch",
        "Smartwatch Fitness Tracker",
        "Wireless Charging Pad",
        "LED Desk Lamp with USB Port",
        "HDMI Cable 6ft",
    ],
    "Clothing": [
        "Classic Crew Neck T-Shirt",
        "Slim Fit Jeans",
        "Hooded Sweatshirt",
        "Waterproof Rain Jacket",
        "Running Shorts",
        "Wool Blend Scarf",
        "Cotton Polo Shirt",
        "Yoga Leggings",
        "Puffer Vest",
        "Denim Jacket",
        "Floral Summer Dress",
        "Chino Pants",
        "Graphic Tee",
        "Fleece Pullover",
        "Long Sleeve Henley",
    ],
    "Home & Garden": [
        "Non-Stick Frying Pan Set",
        "Memory Foam Pillow",
        "Blackout Curtains 2-Pack",
        "Stainless Steel Water Bottle",
        "Robot Vacuum Cleaner",
        "Air Purifier HEPA",
        "Instant Pot 6-Quart",
        "Bamboo Cutting Board",
        "Shower Curtain Liner",
        "LED Smart Bulb 4-Pack",
        "Scented Soy Candle Set",
        "Ceramic Coffee Mug",
        "Garden Kneeler and Seat",
        "Compost Bin for Kitchen",
        "Microfiber Cleaning Cloths",
    ],
    "Sports": [
        "Yoga Mat Non-Slip",
        "Resistance Bands Set",
        "Adjustable Dumbbell 25lb",
        "Jump Rope Speed Cable",
        "Foam Roller for Muscle Recovery",
        "Water Resistant Running Belt",
        "Cycling Gloves",
        "Gym Bag with Wet Pocket",
        "Whey Protein Powder Vanilla",
        "Knee Compression Sleeve",
        "Trekking Poles Collapsible",
        "Tennis Racket Beginner",
        "Swim Goggles Anti-Fog",
        "Insulated Sports Water Bottle",
        "Workout Gloves",
    ],
    "Books": [
        "Atomic Habits",
        "The Lean Startup",
        "Sapiens: A Brief History of Humankind",
        "Thinking Fast and Slow",
        "The Psychology of Money",
        "Deep Work",
        "Zero to One",
        "The Pragmatic Programmer",
        "Clean Code",
        "Educated: A Memoir",
        "The Alchemist",
        "Becoming",
        "1984",
        "Dune",
        "The Power of Now",
    ],
}

FIRST_NAMES = [
    "Alice",
    "Bob",
    "Carlos",
    "Diana",
    "Erik",
    "Fatima",
    "Grace",
    "Hiro",
    "Isabela",
    "James",
    "Kira",
    "Luca",
    "Maya",
    "Noah",
    "Olivia",
    "Pedro",
    "Quinn",
    "Rosa",
    "Sam",
    "Tina",
]
LAST_NAMES = [
    "Smith",
    "Garcia",
    "Müller",
    "Chen",
    "Patel",
    "Martin",
    "Wilson",
    "Anderson",
    "Taylor",
    "Thomas",
    "Hernandez",
    "Moore",
]

# ── Helpers ───────────────────────────────────────────────────────────────────


def rand_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def format_date_messy(d: date) -> str:
    """Randomly return ISO or US format to simulate dirty data."""
    if random.random() < 0.12:  # 12% of dates are in US format
        return d.strftime("%m/%d/%Y")
    return d.isoformat()


# ── Generate products (100 rows) ──────────────────────────────────────────────


def generate_products(n: int = 100):
    rows = []
    # Build a pool of (category, name) pairs, cycling through real names
    pool = []
    for cat, names in PRODUCTS_BY_CATEGORY.items():
        for name in names:
            pool.append((cat, name))
    random.shuffle(pool)

    for i in range(1, n + 1):
        # Cycle through pool; for extra rows beyond pool size, add a variant suffix
        cat, base_name = pool[(i - 1) % len(pool)]
        variant = (
            f" - {random.choice(['Black', 'White', 'Blue', 'Gray', 'Red'])}"
            if i > len(pool)
            else ""
        )
        category = cat
        brand = random.choice(BRANDS)
        price = round(random.uniform(4.99, 499.99), 2)
        rows.append(
            {
                "product_id": f"P{i:04d}",
                "name": base_name + variant,
                "category": category,
                "brand": brand,
                "base_price": price,
            }
        )
    return rows


# ── Generate customers (500 rows) ─────────────────────────────────────────────


def generate_customers(n: int = 500):
    rows = []
    for i in range(1, n + 1):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        email = f"{first.lower()}.{last.lower()}{i}@example.com"
        created = rand_date(date(2021, 1, 1), date(2023, 12, 31))
        rows.append(
            {
                "customer_id": f"C{i:04d}",
                "name": f"{first} {last}",
                "email": email,
                "country": random.choice(COUNTRIES),
                "segment": random.choice(SEGMENTS),
                "created_at": created.isoformat(),
            }
        )
    return rows


# ── Generate orders (5 000 rows + ~2% duplicates) ────────────────────────────


def generate_orders(customers, products, n: int = 5000):
    customer_ids = [c["customer_id"] for c in customers]
    product_ids = [p["product_id"] for p in products]

    rows = []
    for i in range(1, n + 1):
        order_date = rand_date(date(2022, 1, 1), date(2024, 6, 30))
        quantity = random.choice([1, 1, 1, 2, 3, 4, 0, -1])  # 0/-1 are invalid
        customer = random.choice(customer_ids)

        # ~3% of orders have no customer (NULL)
        if random.random() < 0.03:
            customer = ""

        product_id = random.choice(product_ids)
        # Look up price from products list
        product_obj = next(p for p in products if p["product_id"] == product_id)
        unit_price = round(product_obj["base_price"] * random.uniform(0.8, 1.2), 2)

        rows.append(
            {
                "order_id": f"O{i:06d}",
                "customer_id": customer,
                "product_id": product_id,
                "order_date": format_date_messy(order_date),
                "quantity": quantity,
                "unit_price": unit_price,
                "status": random.choice(STATUSES),
            }
        )

    # Add ~2% duplicate rows (same order_id, different position)
    n_dupes = int(n * 0.02)
    dupes = random.sample(rows, n_dupes)
    rows.extend(dupes)
    random.shuffle(rows)
    return rows


# ── Write CSVs ────────────────────────────────────────────────────────────────


def write_csv(filepath: str, rows: list[dict]):
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Written {len(rows):,} rows -> {os.path.basename(filepath)}")


# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Generating synthetic e-commerce dataset...")

    products = generate_products(100)
    customers = generate_customers(500)
    orders = generate_orders(customers, products, 5000)

    write_csv(OUT_PRODUCTS, products)
    write_csv(OUT_CUSTOMERS, customers)
    write_csv(OUT_ORDERS, orders)

    print("\nSummary:")
    print(f"  Products:  {len(products):>6,} rows")
    print(f"  Customers: {len(customers):>6,} rows")
    print(f"  Orders:    {len(orders):>6,} rows (includes ~2% duplicates)")
    print("\nIntentional data quality issues injected into orders_raw.csv only:")
    print("  - Mixed date formats (YYYY-MM-DD and MM/DD/YYYY)")
    print("  - ~3% NULL customer_id")
    print("  - ~2% duplicate order rows")
    print("  - Invalid quantity values (0 and -1)")
    print("\ncustomers_raw.csv and products_raw.csv are clean.")
    print("\nNext step -> run: python setup/ingest.py")
