from fastapi import APIRouter, Depends, HTTPException
from typing import List
from backend.db.database import get_db
from backend.models.schemas import ProductCreate, ProductUpdate, ProductResponse
from backend.services import product_service

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(product: ProductCreate, conn=Depends(get_db)):
    """Add a new product."""
    return product_service.create_product(conn, product)


@router.get("/", response_model=List[ProductResponse])
def get_all_products(conn=Depends(get_db)):
    """Retrieve all products."""
    return product_service.get_products(conn)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, conn=Depends(get_db)):
    """Retrieve a single product by ID."""
    product = product_service.get_product(conn, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, updates: ProductUpdate, conn=Depends(get_db)):
    """Update product fields."""
    product = product_service.update_product(conn, product_id, updates)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.delete("/{product_id}")
def delete_product(product_id: int, conn=Depends(get_db)):
    """Delete a product by ID."""
    success = product_service.delete_product(conn, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": f"Product {product_id} deleted successfully"}
