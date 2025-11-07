from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AddNewProduct(BaseModel):
    tile_image: Optional[str] = None
    tile_category: str
    tile_type: str
    tile_name: str
    tile_description: str
    tile_price: Optional[float] = None
    tile_stock: int
    is_archived: Optional[bool] = None
    
class ProductResponse(AddNewProduct):
    id: int
    pass

class UpdateProduct(BaseModel):
    tile_image: Optional[str] = None
    tile_category: Optional[str] = None
    tile_type: Optional[str] = None
    tile_name: Optional[str] = None
    tile_description: Optional[str] = None
    tile_price: Optional[float] = None
    tile_stock: Optional[int] = None



class Orders(BaseModel):
    product_id:int
    quantity: int
    estimated_delivery: Optional[datetime] = None

class DeliveryAddress(BaseModel):
    house_number: Optional[str]
    street: Optional[str]
    barangay: Optional[str]
    city: Optional[str]
    province: Optional[str]

class OrderResponse(BaseModel): 
    order_id: int
    tile_image: str
    tile_category: str
    tile_type: str
    tile_name: str
    tile_price: float
    quantity: int
    total_price: float
    status: str
    created_at: datetime
    estimated_delivery: Optional[datetime] = None
    delivery_address: Optional[DeliveryAddress] = None
    class Config:
        from_attributes = True

class AddCartItem(BaseModel):
    product_id: int
    quantity: int = 1


class CartItemResponse(BaseModel):
    product_id: int
    tile_image: str
    tile_category: str
    tile_type: str
    tile_name: str
    tile_price: float
    tile_stock: int
    quantity: int
