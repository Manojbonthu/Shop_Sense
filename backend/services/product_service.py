"""
Product CRUD and search — now includes image (base64/url) column.
"""
import psycopg2.extras
from typing import Optional, List, Dict
from backend.models.schemas import ProductCreate, ProductUpdate


def _fetch_all(conn, sql, params=()):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, params)
        return [dict(r) for r in cur.fetchall()]


def _fetch_one(conn, sql, params=()):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, params)
        row = cur.fetchone()
        return dict(row) if row else None


def create_product(conn, product: ProductCreate) -> Dict:
    sql = """
        INSERT INTO products (name, category, price, rating, stock_quantity, description, image)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING *
    """
    result = _fetch_one(conn, sql, (
        product.name, product.category, product.price,
        product.rating, product.stock_quantity, product.description,
        product.image
    ))
    conn.commit()
    return result


def get_products(conn) -> List[Dict]:
    return _fetch_all(conn, "SELECT * FROM products ORDER BY id")


def get_product(conn, product_id: int) -> Optional[Dict]:
    return _fetch_one(conn, "SELECT * FROM products WHERE id = %s", (product_id,))


def update_product(conn, product_id: int, updates: ProductUpdate) -> Optional[Dict]:
    update_data = updates.model_dump(exclude_unset=True)
    if not update_data:
        return get_product(conn, product_id)
    fields = ", ".join(f"{k} = %s" for k in update_data)
    values = list(update_data.values()) + [product_id]
    sql = f"UPDATE products SET {fields} WHERE id = %s RETURNING *"
    result = _fetch_one(conn, sql, values)
    conn.commit()
    return result


def delete_product(conn, product_id: int) -> bool:
    with conn.cursor() as cur:
        cur.execute("DELETE FROM products WHERE id = %s", (product_id,))
        conn.commit()
        return cur.rowcount > 0


def search_products(conn, q=None, category=None, min_price=None, max_price=None, sort=None) -> List[Dict]:
    sql = "SELECT * FROM products WHERE 1=1"
    params = []
    if q:
        sql += " AND (name ILIKE %s OR description ILIKE %s)"
        params += [f"%{q}%", f"%{q}%"]
    if category:
        sql += " AND category ILIKE %s"
        params.append(f"%{category}%")
    if min_price is not None:
        sql += " AND price >= %s"
        params.append(min_price)
    if max_price is not None:
        sql += " AND price <= %s"
        params.append(max_price)
    sort_map = {
        "price_asc":   "price ASC",
        "price_desc":  "price DESC",
        "rating_desc": "rating DESC",
        "rating_asc":  "rating ASC",
    }
    sql += f" ORDER BY {sort_map.get(sort, 'id ASC')}"
    return _fetch_all(conn, sql, params)


def get_autocomplete(conn, q: str) -> List[str]:
    """Return up to 8 product name suggestions matching the query."""
    sql = "SELECT name FROM products WHERE name ILIKE %s ORDER BY rating DESC LIMIT 8"
    with conn.cursor() as cur:
        cur.execute(sql, (f"%{q}%",))
        rows = cur.fetchall()
        return [r[0] for r in rows]
