from pydantic import BaseModel, Field
from typing import Optional, List


# ── PRODUCTS ──────────────────────────────────────────
class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    rating: float = Field(default=0.0, ge=0.0, le=5.0)
    stock_quantity: int = Field(default=0, ge=0)
    description: str = Field(default="")
    image: str = Field(default="")          # base64 or URL


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[float] = Field(None, gt=0)
    rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None
    image: Optional[str] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    category: str
    price: float
    rating: float
    stock_quantity: int
    description: str
    image: str = ""

    class Config:
        from_attributes = True


# ── RECOMMENDATIONS ───────────────────────────────────
class RecommendationRequest(BaseModel):
    category: Optional[str] = None
    max_price: Optional[float] = None
    min_rating: Optional[float] = 0.0


# ── CART ──────────────────────────────────────────────
class CartItem(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)


class CartCheckoutRequest(BaseModel):
    items: List[CartItem]


class CartItemDetail(BaseModel):
    product_id: int
    name: str
    category: str
    unit_price: float
    quantity: int
    item_total: float


class CartCheckoutResponse(BaseModel):
    items: List[CartItemDetail]
    subtotal: float
    discount_percent: float
    discount_amount: float
    tax_percent: float
    tax_amount: float
    final_amount: float


# ── REVIEW ────────────────────────────────────────────
class ReviewAnalyzeRequest(BaseModel):
    review: str = Field(..., min_length=1)


class ReviewAnalyzeResponse(BaseModel):
    sentiment: str
    sentiment_score: float
    positive_words: List[str]
    negative_words: List[str]
    summary: str


# ── PRICE PREDICTION ──────────────────────────────────
class PricePredictRequest(BaseModel):
    category: str
    rating: float = Field(..., ge=0.0, le=5.0)
    stock_quantity: int = Field(..., ge=0)
    description: str = Field(default="")


class PricePredictResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    predicted_price: float
    price_range_low: float
    price_range_high: float
    confidence: str
    similar_products: List[ProductResponse]
    model_features_used: List[str]


# ── AUTH ──────────────────────────────────────────────
class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    role: str
    username: str
    message: str


# ── TRACKING ──────────────────────────────────────────
class TrackViewRequest(BaseModel):
    product_id: int


class TrackCartRequest(BaseModel):
    product_id: int
    product_name: str


# ── ADMIN DASHBOARD ───────────────────────────────────
class DashboardResponse(BaseModel):
    total_products: int
    total_views: int
    total_cart_adds: int
    top_viewed: List[dict]
    top_carted: List[dict]
    category_breakdown: List[dict]
    avg_price_by_category: List[dict]
    price_range_distribution: List[dict]


# ── AUTOCOMPLETE ──────────────────────────────────────
class SuggestResponse(BaseModel):
    suggestions: List[str]
