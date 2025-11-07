from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AdminLogin(BaseModel):
    email: str
    password: str

class ChangePasswordRequest(BaseModel):
    email: str
    new_password: str
    
class OrderAdminUpdate(BaseModel):
    status: str
    estimated_delivery: Optional[datetime] = None


class OrderAdminResponse(BaseModel): 
    order_id: int
    product_id: int
    customer_email:str
    tile_name: str
    tile_price: float
    quantity: int
    status: str
    created_at: datetime
    estimated_delivery: Optional[datetime] = None
    class Config:
        from_attributes = True

class ProductStockUpdate(BaseModel):
    tile_stock: int