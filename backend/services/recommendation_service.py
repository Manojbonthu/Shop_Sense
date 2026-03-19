"""
AI-based product recommendation using TF-IDF + Cosine Similarity (scikit-learn).

Logic:
  1. If category is provided → HARD FILTER to that category first, then rank by TF-IDF + rating
  2. Apply price and rating filters
  3. Rank remaining products by TF-IDF similarity score + rating score
  4. Return top N results
"""
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict
from backend.models.schemas import RecommendationRequest
from backend.services.product_service import get_products


def _clean_products(products: List[Dict]) -> List[Dict]:
    """Convert PostgreSQL Decimal types to plain Python float/int."""
    cleaned = []
    for p in products:
        cleaned.append({
            "id":             int(p["id"]),
            "name":           str(p["name"]),
            "category":       str(p["category"]),
            "price":          float(p["price"]),
            "rating":         float(p["rating"]),
            "stock_quantity": int(p["stock_quantity"]),
            "description":    str(p["description"] or ""),
        })
    return cleaned


def get_recommendations(conn, request: RecommendationRequest, top_n: int = 5) -> List[Dict]:
    raw_products = get_products(conn)

    if not raw_products:
        return []

    all_products = _clean_products(raw_products)
    df = pd.DataFrame(all_products)

    # ── STEP 1: HARD FILTERS (applied before AI scoring) ──────────────────────
    filtered = df.copy()

    # Category: strict hard filter — only show products from requested category
    if request.category:
        cat_mask = filtered["category"].str.lower() == request.category.lower()
        filtered = filtered[cat_mask]
        if filtered.empty:
            # Fallback: try partial match if exact match returns nothing
            cat_mask = filtered["category"].str.lower().str.contains(
                request.category.lower(), na=False
            )
            filtered = df[cat_mask]

    # Price filter
    if request.max_price is not None:
        filtered = filtered[filtered["price"] <= float(request.max_price)]

    # Rating filter
    if request.min_rating is not None and float(request.min_rating) > 0:
        filtered = filtered[filtered["rating"] >= float(request.min_rating)]

    if filtered.empty:
        return []

    # ── STEP 2: TF-IDF SIMILARITY on filtered pool ────────────────────────────
    # Build text corpus from filtered products only
    filtered = filtered.copy()
    filtered["text_corpus"] = (
        filtered["category"].fillna("") + " " +
        filtered["name"].fillna("") + " " +
        filtered["description"].fillna("")
    )

    # Build query: use category + description keywords from request
    query_parts = []
    if request.category:
        query_parts.append(request.category)
    query_text = " ".join(query_parts) if query_parts else "quality product"

    if len(filtered) == 1:
        # Only one product — no need for TF-IDF, just return it
        filtered["score"] = filtered["rating"]
    else:
        try:
            corpus = filtered["text_corpus"].tolist() + [query_text]
            vectorizer = TfidfVectorizer(stop_words="english")
            tfidf_matrix = vectorizer.fit_transform(corpus)

            query_vec = tfidf_matrix[-1]
            product_vecs = tfidf_matrix[:-1]
            similarity_scores = cosine_similarity(query_vec, product_vecs).flatten()
            filtered["similarity"] = similarity_scores
        except Exception:
            filtered["similarity"] = 0.0

        # ── STEP 3: FINAL SCORE = 50% similarity + 50% rating ─────────────────
        max_rating = float(filtered["rating"].max()) or 1.0
        filtered["score"] = (
            filtered["similarity"] * 0.5 +
            (filtered["rating"] / max_rating) * 0.5
        )

    # ── STEP 4: Return top N ──────────────────────────────────────────────────
    top = filtered.nlargest(top_n, "score")
    drop_cols = [c for c in ["text_corpus", "similarity", "score"] if c in top.columns]
    result = top.drop(columns=drop_cols)
    return result.to_dict(orient="records")
