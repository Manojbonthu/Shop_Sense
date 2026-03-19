"""
Admin dashboard analytics — reads from product_views and cart_actions tables.
"""
import psycopg2.extras
from typing import Dict
from backend.models.schemas import DashboardResponse
from backend.services.product_service import get_products


def track_view(conn, product_id: int):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO product_views (product_id) VALUES (%s)", (product_id,))
        conn.commit()


def track_cart(conn, product_id: int, product_name: str):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO cart_actions (product_id, product_name, action) VALUES (%s, %s, 'add')",
            (product_id, product_name)
        )
        conn.commit()


def get_dashboard(conn) -> DashboardResponse:
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:

        # Total products
        cur.execute("SELECT COUNT(*) as cnt FROM products")
        total_products = cur.fetchone()["cnt"]

        # Total views
        cur.execute("SELECT COUNT(*) as cnt FROM product_views")
        total_views = cur.fetchone()["cnt"]

        # Total cart adds
        cur.execute("SELECT COUNT(*) as cnt FROM cart_actions")
        total_cart_adds = cur.fetchone()["cnt"]

        # Top 5 viewed products
        cur.execute("""
            SELECT p.name, COUNT(v.id) as views
            FROM product_views v
            JOIN products p ON p.id = v.product_id
            GROUP BY p.name ORDER BY views DESC LIMIT 5
        """)
        top_viewed = [dict(r) for r in cur.fetchall()]

        # Top 5 carted products
        cur.execute("""
            SELECT product_name as name, COUNT(id) as cart_adds
            FROM cart_actions
            GROUP BY product_name ORDER BY cart_adds DESC LIMIT 5
        """)
        top_carted = [dict(r) for r in cur.fetchall()]

        # Category breakdown (product count)
        cur.execute("""
            SELECT category, COUNT(*) as count
            FROM products GROUP BY category ORDER BY count DESC
        """)
        category_breakdown = [dict(r) for r in cur.fetchall()]

        # Avg price by category
        cur.execute("""
            SELECT category, ROUND(AVG(price)::numeric, 2) as avg_price
            FROM products GROUP BY category ORDER BY avg_price DESC
        """)
        avg_price_by_category = [dict(r) for r in cur.fetchall()]

        # Price range distribution
        cur.execute("""
            SELECT
              CASE
                WHEN price < 1000   THEN 'Under ₹1K'
                WHEN price < 5000   THEN '₹1K–5K'
                WHEN price < 20000  THEN '₹5K–20K'
                WHEN price < 100000 THEN '₹20K–1L'
                ELSE 'Above ₹1L'
              END as range,
              COUNT(*) as count
            FROM products
            GROUP BY range ORDER BY MIN(price)
        """)
        price_range_distribution = [dict(r) for r in cur.fetchall()]

    return DashboardResponse(
        total_products=total_products,
        total_views=total_views,
        total_cart_adds=total_cart_adds,
        top_viewed=top_viewed,
        top_carted=top_carted,
        category_breakdown=category_breakdown,
        avg_price_by_category=avg_price_by_category,
        price_range_distribution=price_range_distribution
    )
