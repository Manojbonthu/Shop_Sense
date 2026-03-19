from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from backend.db.database import get_db
from backend.models.schemas import (
    ProductResponse,
    RecommendationRequest,
    CartCheckoutRequest, CartCheckoutResponse,
    ReviewAnalyzeRequest, ReviewAnalyzeResponse,
)
from backend.services import product_service, recommendation_service, cart_service, review_service

search_router    = APIRouter(tags=["Search"])
recommend_router = APIRouter(tags=["AI Recommendations"])
cart_router      = APIRouter(prefix="/cart",   tags=["Cart"])
review_router    = APIRouter(prefix="/review", tags=["Review Sentiment"])


@search_router.get("/search", response_model=List[ProductResponse])
def search_products(
    q:          Optional[str]   = Query(None, description="Keyword (name or description)"),
    category:   Optional[str]   = Query(None, description="Filter by category"),
    min_price:  Optional[float] = Query(None, description="Minimum price"),
    max_price:  Optional[float] = Query(None, description="Maximum price"),
    sort:       Optional[str]   = Query(None, description="price_asc | price_desc | rating_desc | rating_asc"),
    conn=Depends(get_db)
):
    """Search and filter products."""
    return product_service.search_products(conn, q=q, category=category,
                                           min_price=min_price, max_price=max_price, sort=sort)


@recommend_router.post("/recommend", response_model=List[ProductResponse])
def recommend_products(request: RecommendationRequest, conn=Depends(get_db)):
    """AI-powered product recommendations (TF-IDF + cosine similarity)."""
    return recommendation_service.get_recommendations(conn, request)


@cart_router.post("/checkout", response_model=CartCheckoutResponse)
def checkout(request: CartCheckoutRequest, conn=Depends(get_db)):
    """Calculate cart total with discount and tax."""
    return cart_service.calculate_checkout(conn, request)


@review_router.post("/analyze", response_model=ReviewAnalyzeResponse)
def analyze_review(request: ReviewAnalyzeRequest):
    """Analyze product review sentiment using NLP."""
    return review_service.analyze_review(request)
