import nltk
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('brown', quiet=True)

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.db.database import init_db
from backend.routes.products import router as products_router
from backend.routes.other import search_router, recommend_router, cart_router, review_router
from backend.routes.new_routes import (
    auth_router, predict_router, similar_router,
    suggest_router, dashboard_router, track_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        init_db()
        from seed_data import seed
        seed()
    except Exception as e:
        print(f"Startup error: {e}")
    yield


app = FastAPI(
    title="ShopSense",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products_router)
app.include_router(search_router)
app.include_router(recommend_router)
app.include_router(cart_router)
app.include_router(review_router)
app.include_router(auth_router)
app.include_router(predict_router)
app.include_router(similar_router)
app.include_router(suggest_router)
app.include_router(dashboard_router)
app.include_router(track_router)

app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/", include_in_schema=False)
def serve_frontend():
    return FileResponse("frontend/index.html")


@app.get("/health")
def health():
    return {"status": "ok"}
