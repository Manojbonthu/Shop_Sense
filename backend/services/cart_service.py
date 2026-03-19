"""
Cart checkout: calculates subtotal, discount, tax, and final payable amount.

Business Rules:
  - Subtotal > 5000  -> 10% discount
  - Any Electronics  -> 5% tax on discounted amount
"""
from typing import List
from fastapi import HTTPException
from backend.models.schemas import (
    CartCheckoutRequest, CartCheckoutResponse, CartItemDetail
)
from backend.services.product_service import get_product

ELECTRONICS_CATEGORIES = {"electronics", "gadgets", "tech", "computers", "mobiles", "phones"}


def calculate_checkout(conn, request: CartCheckoutRequest) -> CartCheckoutResponse:
    items_detail: List[CartItemDetail] = []
    subtotal = 0.0
    has_electronics = False

    for item in request.items:
        product = get_product(conn, item.product_id)

        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product with id {item.product_id} not found"
            )

        stock = int(product["stock_quantity"])
        if stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for '{product['name']}'. Available: {stock}"
            )

        unit_price = float(product["price"])
        item_total = unit_price * item.quantity
        subtotal += item_total

        if product["category"].lower() in ELECTRONICS_CATEGORIES:
            has_electronics = True

        items_detail.append(CartItemDetail(
            product_id=int(product["id"]),
            name=str(product["name"]),
            category=str(product["category"]),
            unit_price=unit_price,
            quantity=item.quantity,
            item_total=round(item_total, 2)
        ))

    # Discount: 10% if subtotal > 5000
    discount_percent = 10.0 if subtotal > 5000 else 0.0
    discount_amount = round(subtotal * discount_percent / 100, 2)
    discounted = subtotal - discount_amount

    # Tax: 5% if any Electronics in cart
    tax_percent = 5.0 if has_electronics else 0.0
    tax_amount = round(discounted * tax_percent / 100, 2)

    final_amount = round(discounted + tax_amount, 2)

    return CartCheckoutResponse(
        items=items_detail,
        subtotal=round(subtotal, 2),
        discount_percent=discount_percent,
        discount_amount=discount_amount,
        tax_percent=tax_percent,
        tax_amount=tax_amount,
        final_amount=final_amount
    )
