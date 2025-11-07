from fastapi import APIRouter, Depends, HTTPException, Cookie
from sqlalchemy.orm import Session
from database.ProductTable import Carts as CartModel
from models.ProductModel import AddCartItem, CartItemResponse
from DatabaseConnector import get_db

router = APIRouter(prefix="/cart", tags=["Cart"])


# ---------------- GET CART ITEMS ----------------
@router.get("/", response_model=list[CartItemResponse])
def get_cart_items(user_email: str = Cookie(None), db: Session = Depends(get_db)):
    if not user_email:
        raise HTTPException(status_code=401, detail="User not authenticated")

    cart_items = db.query(CartModel).filter(CartModel.user_email == user_email).all()

    return [
        CartItemResponse(
            product_id=item.product_id,
            tile_image=item.product.tile_image or "",
            tile_category=item.product.tile_category or "",
            tile_type=item.product.tile_type or "",
            tile_name=item.product.tile_name,
            tile_price=item.product.tile_price,
            tile_stock=item.product.tile_stock,
            quantity=item.quantity
        )
        for item in cart_items
    ]

@router.post("/add", response_model=CartItemResponse)
def add_to_cart(item: AddCartItem, user_email: str = Cookie(None), db: Session = Depends(get_db)):
    if not user_email:
        raise HTTPException(status_code=401, detail="User not authenticated")

    # Use filter instead of filter_by for clarity
    existing_item = db.query(CartModel).filter(
        CartModel.user_email == user_email,
        CartModel.product_id == item.product_id
    ).first()

    if existing_item:
        # Increment quantity if already in cart
        existing_item.quantity += item.quantity
        db.commit()
        db.refresh(existing_item)
        cart_item = existing_item
    else:
        # Add new item to cart
        cart_item = CartModel(
            user_email=user_email,
            product_id=item.product_id,
            quantity=item.quantity
        )
        db.add(cart_item)
        db.commit()
        db.refresh(cart_item)

    return CartItemResponse(
        product_id=cart_item.product_id,
        tile_image=cart_item.product.tile_image or "",
        tile_category=cart_item.product.tile_category or "",
        tile_type=cart_item.product.tile_type or "",
        tile_name=cart_item.product.tile_name,
        tile_price=cart_item.product.tile_price,
        tile_stock=cart_item.product.tile_stock,
        quantity=cart_item.quantity
    )

# ---------------- DELETE FROM CART ----------------
@router.delete("/delete/{product_id}", response_model=dict)
def delete_from_cart(product_id: int, user_email: str = Cookie(None), db: Session = Depends(get_db)):
    if not user_email:
        raise HTTPException(status_code=401, detail="User not authenticated")

    cart_item = db.query(CartModel).filter_by(
        user_email=user_email, product_id=product_id
    ).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    db.delete(cart_item)
    db.commit()

    return {"detail": "Cart item removed successfully"}
