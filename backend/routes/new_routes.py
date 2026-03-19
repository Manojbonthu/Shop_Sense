"""
New routes: auth, price prediction, similar products, autocomplete, dashboard, tracking
"""
from fastapi import APIRouter, Depends
from backend.db.database import get_db
from backend.models.schemas import (
    LoginRequest, LoginResponse,
    PricePredictRequest, PricePredictResponse,
    ProductResponse, SuggestResponse,
    TrackViewRequest, TrackCartRequest,
    DashboardResponse
)
from backend.services import (
    auth_service, price_prediction_service,
    similar_service, dashboard_service, product_service
)
from typing import List

auth_router      = APIRouter(prefix="/auth",    tags=["Auth"])
predict_router   = APIRouter(prefix="/predict", tags=["Price Prediction"])
similar_router   = APIRouter(tags=["Similar Products"])
suggest_router   = APIRouter(tags=["Autocomplete"])
dashboard_router = APIRouter(prefix="/admin",   tags=["Admin Dashboard"])
track_router     = APIRouter(prefix="/track",   tags=["Tracking"])


# ── AUTH ──────────────────────────────────────────────
@auth_router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    """Login — admin/admin123 for admin, any credentials for customer."""
    return auth_service.login(request)


# ── PRICE PREDICTION ──────────────────────────────────
@predict_router.post("/price", response_model=PricePredictResponse)
def predict_price(request: PricePredictRequest, conn=Depends(get_db)):
    """Predict product price using Linear Regression on catalog data."""
    return price_prediction_service.predict_price(conn, request)


# ── SIMILAR PRODUCTS ──────────────────────────────────
@similar_router.get("/products/{product_id}/similar", response_model=List[ProductResponse])
def similar_products(product_id: int, conn=Depends(get_db)):
    """Get similar products using TF-IDF cosine similarity."""
    return similar_service.get_similar_products(conn, product_id)


# ── AUTOCOMPLETE ──────────────────────────────────────
@suggest_router.get("/search/suggest", response_model=SuggestResponse)
def suggest(q: str = "", conn=Depends(get_db)):
    """Return autocomplete suggestions for product search."""
    if not q or len(q) < 2:
        return SuggestResponse(suggestions=[])
    suggestions = product_service.get_autocomplete(conn, q)
    return SuggestResponse(suggestions=suggestions)


# ── TRACKING ──────────────────────────────────────────
@track_router.post("/view")
def track_view(request: TrackViewRequest, conn=Depends(get_db)):
    dashboard_service.track_view(conn, request.product_id)
    return {"ok": True}


@track_router.post("/cart")
def track_cart(request: TrackCartRequest, conn=Depends(get_db)):
    dashboard_service.track_cart(conn, request.product_id, request.product_name)
    return {"ok": True}


# ── ADMIN DASHBOARD ───────────────────────────────────
@dashboard_router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(conn=Depends(get_db)):
    """Admin analytics dashboard."""
    return dashboard_service.get_dashboard(conn)
