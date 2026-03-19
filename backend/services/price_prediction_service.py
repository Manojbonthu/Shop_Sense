"""
Price Prediction using Linear Regression (scikit-learn).

Pipeline:
  1. Load all products from DB
  2. Feature engineering: OneHotEncode category + TF-IDF description + rating + stock
  3. Train LinearRegression on existing products
  4. Predict price for new input
  5. Return predicted price, confidence range, similar products
"""
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
import scipy.sparse as sp
from typing import Dict, List

from backend.models.schemas import PricePredictRequest, PricePredictResponse, ProductResponse
from backend.services.product_service import get_products


CATEGORIES = [
    "Electronics", "Footwear", "Clothing",
    "Kitchen Appliances", "Beauty & Personal Care", "Sports & Outdoors"
]


def _build_features(df: pd.DataFrame):
    """
    Build feature matrix from product DataFrame.
    Returns: sparse feature matrix X, fitted transformers
    """
    # One-hot encode category
    ohe = OneHotEncoder(categories=[CATEGORIES], handle_unknown='ignore', sparse_output=True)
    cat_encoded = ohe.fit_transform(df[["category"]])

    # TF-IDF on description (max 30 features to keep it small with 20 products)
    tfidf = TfidfVectorizer(max_features=30, stop_words="english")
    desc_tfidf = tfidf.fit_transform(df["description"].fillna(""))

    # Numeric features: rating, stock_quantity
    numeric = df[["rating", "stock_quantity"]].values.astype(float)
    scaler = StandardScaler()
    numeric_scaled = scaler.fit_transform(numeric)

    # Combine all features
    X = sp.hstack([
        cat_encoded,
        desc_tfidf,
        sp.csr_matrix(numeric_scaled)
    ])

    return X, ohe, tfidf, scaler


def _transform_input(request: PricePredictRequest, ohe, tfidf, scaler):
    """Transform a single prediction request using fitted transformers."""
    # Category
    cat_df = pd.DataFrame({"category": [request.category]})
    cat_encoded = ohe.transform(cat_df[["category"]])

    # Description TF-IDF
    desc_tfidf = tfidf.transform([request.description or ""])

    # Numeric
    numeric = np.array([[request.rating, request.stock_quantity]], dtype=float)
    numeric_scaled = scaler.transform(numeric)

    X_new = sp.hstack([cat_encoded, desc_tfidf, sp.csr_matrix(numeric_scaled)])
    return X_new


def predict_price(conn, request: PricePredictRequest) -> PricePredictResponse:
    # Load all products from DB
    raw = get_products(conn)
    if not raw:
        raise ValueError("No products in database to train on")

    df = pd.DataFrame([{
        "id":             int(p["id"]),
        "name":           str(p["name"]),
        "category":       str(p["category"]),
        "price":          float(p["price"]),
        "rating":         float(p["rating"]),
        "stock_quantity": int(p["stock_quantity"]),
        "description":    str(p["description"] or ""),
        "image":          str(p.get("image") or ""),
    } for p in raw])

    y = df["price"].values

    # Build features and train
    X, ohe, tfidf, scaler = _build_features(df)
    model = LinearRegression()
    model.fit(X, y)

    # Transform user input
    X_new = _transform_input(request, ohe, tfidf, scaler)
    predicted = float(model.predict(X_new)[0])
    predicted = max(predicted, 100.0)   # floor at ₹100

    # Confidence range: ±25% (reflects small dataset uncertainty)
    margin = predicted * 0.25
    low  = round(max(predicted - margin, 50.0), 2)
    high = round(predicted + margin, 2)
    predicted = round(predicted, 2)

    # Confidence label based on how well training data covers this category
    cat_count = len(df[df["category"].str.lower() == request.category.lower()])
    if cat_count >= 4:
        confidence = "Medium"
    elif cat_count >= 2:
        confidence = "Low-Medium"
    else:
        confidence = "Low (few training samples)"

    # Similar products: within ±40% of predicted price in same category
    similar_df = df[
        (df["category"].str.lower() == request.category.lower()) &
        (df["price"] >= predicted * 0.6) &
        (df["price"] <= predicted * 1.4)
    ].nlargest(3, "rating")

    similar = [
        ProductResponse(
            id=int(r["id"]), name=r["name"], category=r["category"],
            price=float(r["price"]), rating=float(r["rating"]),
            stock_quantity=int(r["stock_quantity"]),
            description=r["description"], image=r["image"]
        )
        for _, r in similar_df.iterrows()
    ]

    features_used = [
        "Category (One-Hot Encoded)",
        "Description (TF-IDF, 30 features)",
        "Rating (StandardScaler)",
        "Stock Quantity (StandardScaler)",
    ]

    return PricePredictResponse(
        predicted_price=predicted,
        price_range_low=low,
        price_range_high=high,
        confidence=confidence,
        similar_products=similar,
        model_features_used=features_used
    )
