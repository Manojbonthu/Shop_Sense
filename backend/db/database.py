"""
PostgreSQL database connection using psycopg2 (no ORM).
Update DB_CONFIG with your own PostgreSQL credentials.
"""
import psycopg2
import psycopg2.extras

DB_CONFIG = {
    "host":     "aws-1-ap-southeast-1.pooler.supabase.com",
    "port":     5432,
    "dbname":   "postgres",
    "user":     "postgres.jlevlrygmlvypqhbbixk",
    "password": "Manoj@bonthu9",
    "sslmode":  "require",
}


def get_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    return conn


def get_db():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Create / migrate all tables."""
    conn = get_connection()
    cur = conn.cursor()

    # Products table — add image column if missing
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id              SERIAL PRIMARY KEY,
            name            VARCHAR(255)    NOT NULL,
            category        VARCHAR(100)    NOT NULL,
            price           NUMERIC(12, 2)  NOT NULL,
            rating          NUMERIC(3, 1)   DEFAULT 0.0,
            stock_quantity  INTEGER         DEFAULT 0,
            description     TEXT            DEFAULT '',
            image           TEXT            DEFAULT ''
        );
    """)
    # Add image column to existing table if it doesn't exist
    cur.execute("""
        ALTER TABLE products ADD COLUMN IF NOT EXISTS image TEXT DEFAULT '';
    """)

    # User sessions table (simple — no real auth, just role tracking)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_sessions (
            id          SERIAL PRIMARY KEY,
            username    VARCHAR(100) NOT NULL,
            role        VARCHAR(20)  NOT NULL DEFAULT 'customer',
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Product views tracking (for admin dashboard)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS product_views (
            id          SERIAL PRIMARY KEY,
            product_id  INTEGER NOT NULL,
            viewed_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Cart actions tracking (for admin dashboard)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cart_actions (
            id          SERIAL PRIMARY KEY,
            product_id  INTEGER NOT NULL,
            product_name VARCHAR(255),
            action      VARCHAR(20) DEFAULT 'add',
            actioned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    cur.close()
    conn.close()
