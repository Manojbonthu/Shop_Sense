"""
Seed the PostgreSQL database with 20 sample products.
Run: python seed_data.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.db.database import get_connection

SAMPLE_PRODUCTS = [
    ("Sony WH-1000XM5 Headphones",      "Electronics",           24999, 4.8, 50,
     "Industry-leading noise cancelling wireless headphones with 30-hour battery life and exceptional sound quality."),
    ("Apple iPhone 15",                  "Electronics",           79999, 4.7, 30,
     "Latest Apple smartphone with A16 Bionic chip, advanced camera system, and all-day battery."),
    ("Samsung Galaxy S24",               "Electronics",           69999, 4.6, 40,
     "Flagship Android phone with AI features, 200MP camera, and Snapdragon 8 Gen 3 processor."),
    ("Boat Rockerz 450 Headphones",      "Electronics",            1499, 4.1, 200,
     "On-ear wireless headphones with 15-hour playback, deep bass, and built-in mic."),
    ("Dell XPS 15 Laptop",               "Electronics",          149999, 4.7, 15,
     "Premium laptop with Intel Core i7, 16GB RAM, 512GB SSD, and OLED display."),
    ("Lenovo IdeaPad Slim 5",            "Electronics",           52999, 4.3, 25,
     "Lightweight everyday laptop with AMD Ryzen 5, 8GB RAM, and 12-hour battery life."),
    ("Zebronics 24 Inch Monitor",        "Electronics",           11999, 4.3, 35,
     "Full HD IPS monitor with 75Hz refresh rate, HDMI port, and eye care technology."),
    ("Logitech MX Master 3 Mouse",       "Electronics",            8995, 4.8, 55,
     "Advanced wireless mouse with MagSpeed scroll, ergonomic shape, and 70-day battery."),
    ("Nike Air Max 270",                 "Footwear",              12995, 4.5, 80,
     "Stylish running shoes with Max Air cushioning unit for all-day comfort and support."),
    ("Adidas Ultraboost 22",             "Footwear",              14999, 4.6, 60,
     "High-performance running shoes with Boost cushioning and Primeknit upper fabric."),
    ("Puma Men's Casual Sneakers",       "Footwear",               3999, 4.0, 120,
     "Lightweight casual sneakers for everyday wear with breathable mesh and rubber sole."),
    ("Prestige 2000W Induction Cooktop", "Kitchen Appliances",     3299, 4.4, 70,
     "2000W induction cooktop with 8 preset menus, touch panel, and auto shut-off."),
    ("Philips Air Fryer HD9252",         "Kitchen Appliances",     8999, 4.5, 45,
     "Rapid air technology fryer with 1.8L capacity, adjustable timer and temperature."),
    ("Milton Thermosteel Flask 1L",      "Kitchen Appliances",      699, 4.2, 300,
     "Stainless steel flask that keeps drinks hot for 24 hours and cold for 48 hours."),
    ("Levi's 511 Slim Fit Jeans",        "Clothing",               3499, 4.4, 150,
     "Classic slim fit jeans in stretch denim, comfortable and versatile for any occasion."),
    ("Allen Solly Formal Shirt",         "Clothing",               1299, 4.2, 200,
     "Cotton formal shirt with regular fit, ideal for office and semi-formal occasions."),
    ("Peter England Blazer",             "Clothing",               4999, 4.3, 40,
     "Single-breasted formal blazer in premium wool blend, perfect for business meetings."),
    ("Himalaya Neem Face Wash",          "Beauty & Personal Care",  185, 4.3, 500,
     "Purifying neem face wash that removes excess oil and prevents pimples naturally."),
    ("The Ordinary Niacinamide Serum",   "Beauty & Personal Care",  699, 4.5, 120,
     "10% Niacinamide + 1% Zinc serum that visibly reduces blemishes and congestion."),
    ("Wildcraft 45L Trekking Backpack",  "Sports & Outdoors",      2999, 4.4, 60,
     "Water-resistant hiking backpack with adjustable straps, multiple compartments, and rain cover."),
]


def seed():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM products")
    count = cur.fetchone()[0]
    if count > 0:
        print(f"Already has {count} products. Skipping seed.")
        cur.close(); conn.close()
        return
    cur.executemany("""
        INSERT INTO products (name, category, price, rating, stock_quantity, description)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, SAMPLE_PRODUCTS)
    conn.commit()
    print(f"✅ Seeded {len(SAMPLE_PRODUCTS)} products successfully.")
    cur.close()
    conn.close()


if __name__ == "__main__":
    seed()
