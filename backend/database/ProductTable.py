from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum,Boolean
from sqlalchemy.orm import relationship
from DatabaseConnector import Base
from datetime import datetime
import enum
import tools

# ---------------- ENUM ----------------
class OrderStatus(enum.Enum):
    Pending = "Pending"
    Approved = "Approved"
    Shipped = "Shipped"
    Rejected = "Rejected"

# ---------------- PRODUCT ----------------
class Products(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    tile_image = Column(String, nullable=True)
    tile_category = Column(String, nullable=True)
    tile_type = Column(String, nullable=True)
    tile_name = Column(String, nullable=False)
    tile_description = Column(String, nullable=True)
    tile_price = Column(Float, nullable=False)
    tile_stock = Column(Integer, default=0)
    is_archived = Column(Boolean, default=False)

    # Relationships
    cart_items = relationship("Carts", back_populates="product", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="product", cascade="all, delete-orphan")
    stock_records = relationship("StockRecord", back_populates="product", cascade="all, delete-orphan")


# ---------------- CART ----------------
class Carts(Base):
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)

    product = relationship("Products", back_populates="cart_items")


# ---------------- ORDER ----------------
class Orders(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(tools.PH_TZ))
    status = Column(Enum(OrderStatus), default=OrderStatus.Pending, nullable=False)
    estimated_delivery = Column(DateTime, nullable=True)

    # Address snapshot fields
    house_number = Column(String, nullable=True)
    street = Column(String, nullable=True)
    barangay = Column(String, nullable=True)
    city = Column(String, nullable=True)
    province = Column(String, nullable=True)

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


# ---------------- ORDER ITEM ----------------
class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)

    # Snapshot of product details at order time
    tile_name = Column(String, nullable=False)
    tile_category = Column(String, nullable=True)
    tile_type = Column(String, nullable=True)
    tile_image = Column(String, nullable=True)
    tile_price = Column(Float, nullable=False)

    order = relationship("Orders", back_populates="items")
    product = relationship("Products", back_populates="order_items")


# ---------------- ORDER LOG ----------------
class OrderLog(Base):
    __tablename__ = "order_logs"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, nullable=False)
    user_email = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(tools.PH_TZ))
    status = Column(Enum(OrderStatus), nullable=False)
    estimated_delivery = Column(DateTime, nullable=True)

    # Address snapshot
    house_number = Column(String, nullable=True)
    street = Column(String, nullable=True)
    barangay = Column(String, nullable=True)
    city = Column(String, nullable=True)
    province = Column(String, nullable=True)

    # Product snapshot
    product_id = Column(Integer, nullable=False)
    tile_name = Column(String, nullable=False)
    tile_category = Column(String, nullable=True)
    tile_type = Column(String, nullable=True)
    tile_image = Column(String, nullable=True)
    tile_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)


# ---------------- SALES ----------------
class Sales(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    customer_email = Column(String, nullable=False)
    tile_name = Column(String, nullable=False)
    tile_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(tools.PH_TZ))

# ---------------- STOCK RECORD ----------------
class StockRecord(Base):
    __tablename__ = "stock_records"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    change_type = Column(String, nullable=False)  # "add" or "update"
    quantity_changed = Column(Integer, nullable=False)
    previous_stock = Column(Integer, nullable=False)
    new_stock = Column(Integer, nullable=False)  
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(tools.PH_TZ))

    # Relationship
    product = relationship("Products", back_populates="stock_records")
