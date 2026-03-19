"""
Similar Products — finds top N most similar products using cosine similarity
on TF-IDF of (category + name + description).
"""
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict
from backend.services.product_service import get_products


def get_similar_products(conn, product_id: int, top_n: int = 4) -> List[Dict]:
    raw = get_products(conn)
    if not raw:
        return []

    products = [{
        "id":             int(p["id"]),
        "name":           str(p["name"]),
        "category":       str(p["category"]),
        "price":          float(p["price"]),
        "rating":         float(p["rating"]),
        "stock_quantity": int(p["stock_quantity"]),
        "description":    str(p["description"] or ""),
        "image":          str(p.get("image") or ""),
    } for p in raw]

    df = pd.DataFrame(products)

    # Find target product
    target_rows = df[df["id"] == product_id]
    if target_rows.empty:
        return []

    # Build corpus
    df["corpus"] = df["category"] + " " + df["name"] + " " + df["description"].fillna("")

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(df["corpus"])

    # Get target index
    target_idx = df.index[df["id"] == product_id][0]
    target_vec = tfidf_matrix[target_idx]

    # Similarity scores
    scores = cosine_similarity(target_vec, tfidf_matrix).flatten()
    df["similarity"] = scores

    # Exclude the product itself, return top N
    similar = df[df["id"] != product_id].nlargest(top_n, "similarity")
    return similar.drop(columns=["corpus", "similarity"]).to_dict(orient="records")
