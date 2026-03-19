# ShopSense — Mini E-Commerce Platform with AI Features

FastAPI + PostgreSQL backend with an AI-powered frontend.

---

## Project Structure

```
ecommerce/
├── main.py                          # FastAPI app entry point
├── seed_data.py                     # Seeds 20 sample products into DB
├── requirements.txt
│
├── backend/
│   ├── db/
│   │   └── database.py              # psycopg2 connection + init_db()
│   ├── models/
│   │   ├── product_model.py         # Table field reference (no ORM)
│   │   └── schemas.py               # Pydantic request/response models
│   ├── routes/
│   │   ├── products.py              # CRUD: POST/GET/PUT/DELETE /products
│   │   └── other.py                 # /search  /recommend  /cart/checkout  /review/analyze
│   └── services/
│       ├── product_service.py       # Raw SQL CRUD + search
│       ├── recommendation_service.py# TF-IDF + cosine similarity (scikit-learn)
│       ├── cart_service.py          # Discount + tax calculation
│       └── review_service.py        # Sentiment analysis (TextBlob)
│
└── frontend/
    └── index.html                   # Single-page UI (HTML + CSS + JS)
```

---

## Step 1 — PostgreSQL Setup (pgAdmin)

1. Open **pgAdmin** and connect to your PostgreSQL server.
2. Right-click **Databases → Create → Database**.
3. Name it `ecommerce_db` and save.
4. Open `backend/db/database.py` and update:

```python
DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "ecommerce_db",
    "user":     "postgres",
    "password": "YOUR_PASSWORD_HERE",   # ← change this
}
```

---

## Step 2 — Install Dependencies

```bash
pip install -r requirements.txt
python -m textblob.download_corpora
```

---

## Step 3 — Run the Server

```bash
cd ecommerce
uvicorn main:app --reload --port 8000
```

On first run the app will:
- Auto-create the `products` table in PostgreSQL
- Seed 20 sample products automatically

---

## Step 4 — Open in Browser

| URL | Description |
|-----|-------------|
| http://localhost:8000 | Frontend UI |
| http://localhost:8000/docs | Swagger API docs |
| http://localhost:8000/redoc | ReDoc API docs |

---

## API Endpoints

### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/products/` | Add a new product |
| GET | `/products/` | Get all products |
| GET | `/products/{id}` | Get single product |
| PUT | `/products/{id}` | Update product |
| DELETE | `/products/{id}` | Delete product |

### Search
```
GET /search?q=headphones&category=Electronics&min_price=1000&max_price=50000&sort=price_asc
```

### AI Recommendations
```
POST /recommend
Body: { "category": "Electronics", "max_price": 10000, "min_rating": 4.0 }
```

### Cart Checkout
```
POST /cart/checkout
Body: { "items": [{ "product_id": 1, "quantity": 2 }, { "product_id": 3, "quantity": 1 }] }
```
Rules: subtotal > ₹5000 → 10% discount | Electronics in cart → 5% tax

### Review Sentiment
```
POST /review/analyze
Body: { "review": "Amazing sound quality but the battery life is average." }
```

---

## AI Features

**Recommendation Engine** — TF-IDF (scikit-learn) builds a text corpus from product name + category + description, then ranks products by cosine similarity to the user query, blended with a rating score.

**Sentiment Analysis** — TextBlob NLP scores review polarity from -1.0 (very negative) to +1.0 (very positive) and classifies as Positive / Neutral / Negative with keyword extraction.

---

## Business Rules
- Cart subtotal **> ₹5,000** → **10% discount** applied
- Cart contains **Electronics** → **5% tax** on discounted amount
- Checkout validates **stock availability** and raises 400 if insufficient
