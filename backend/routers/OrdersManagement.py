from DatabaseConnector import get_db
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Cookie

from models.ProductModel import Orders as OrdersModel, OrderResponse,DeliveryAddress
from database.ProductTable import Orders as TableOrders, OrderItem, OrderStatus, Products,OrderLog as TableOrderLog
from database.AdminTable import RecentActivity
from database.UserTable import Address, User  
import tools
from datetime import datetime

router = APIRouter(prefix="/orders", tags=["Cart & Orders"])


# =========================
# 🛒 Add Order (with active address)
# =========================

@router.post("/add-order", response_model=OrderResponse)
def add_order(order_data: OrdersModel, user_email: str = Cookie(None), db: Session = Depends(get_db)):
    if not user_email:
        raise HTTPException(status_code=401, detail="User not found")

    # ✅ Get product
    product = db.query(Products).filter(Products.id == order_data.product_id).with_for_update().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # ✅ Get user
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ✅ Get active address
    active_address = db.query(Address).filter(Address.user_id == user.id, Address.is_active == True).first()
    if not active_address:
        raise HTTPException(status_code=400, detail="No active address found. Please set one before ordering.")

    # ✅ Create order
    order = TableOrders(
        user_email=user_email,
        status=OrderStatus.Pending,
        house_number=active_address.house_number,
        street=active_address.street,
        barangay=active_address.barangay,
        city=active_address.city,
        province=active_address.province,
    )
    db.add(order)
    db.flush()  # generate order.id without committing yet

    # ✅ Create order item
    new_item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        quantity=order_data.quantity,
        tile_name=product.tile_name,
        tile_category=product.tile_category,
        tile_type=product.tile_type,
        tile_price=product.tile_price,
        tile_image=product.tile_image
    )
    db.add(new_item)

    # ✅ Commit everything together
    db.commit()
    db.refresh(product)
    db.refresh(order)
    db.refresh(new_item)

    # ✅ Log recent activity
    activity = RecentActivity(
        email=user_email,
        activity=f"Placed an order #{order.id}",
        created_at=datetime.now(tools.PH_TZ)
    )
    db.add(activity)
    db.commit()

    # ✅ Return response
    return OrderResponse(
        order_id=order.id,
        status=order.status.value,
        created_at=order.created_at,
        estimated_delivery=order.estimated_delivery,
        tile_image=product.tile_image,
        tile_category=product.tile_category,
        tile_type=product.tile_type,
        tile_name=product.tile_name,
        tile_price=product.tile_price,
        quantity=new_item.quantity,
        total_price=product.tile_price * new_item.quantity,
        delivery_address=DeliveryAddress(
            house_number=order.house_number,
            street=order.street,
            barangay=order.barangay,
            city=order.city,
            province=order.province,
        )
    )

# =========================
# 📦 Get Orders (with address)
# =========================
@router.get("/", response_model=list[OrderResponse])
def get_orders(
    db: Session = Depends(get_db),
    user_email: str = Cookie(None)
):
    if not user_email:
        raise HTTPException(status_code=401, detail="Missing user email cookie")

    # Exclude orders with status "Shipped" or "Rejected"
    orders = (
        db.query(TableOrders)
        .filter(
            TableOrders.user_email == user_email,
            ~TableOrders.status.in_(["Shipped", "Rejected"])  # <-- exclude these
        )
        .order_by(TableOrders.created_at.desc())
        .all()
    )

    if not orders:
        raise HTTPException(status_code=404, detail="No orders found for this user")

    responses = []
    for order in orders:
        order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        for item in order_items:
            responses.append(
                OrderResponse(
                    order_id=order.id,
                    status=order.status.value,
                    created_at=order.created_at,
                    estimated_delivery=order.estimated_delivery,
                    tile_image=item.tile_image,
                    tile_category=item.tile_category,
                    tile_type=item.tile_type,
                    tile_name=item.tile_name,
                    tile_price=item.tile_price,
                    quantity=item.quantity,
                    total_price=item.tile_price * item.quantity,
                    delivery_address=DeliveryAddress(
                        house_number=order.house_number,
                        street=order.street,
                        barangay=order.barangay,
                        city=order.city,
                        province=order.province,
                    )
                )
            )

    return responses


@router.get("/logs", response_model=list[OrderResponse])
def get_order_logs(
    db: Session = Depends(get_db),
    user_email: str = Cookie(None)
):
    if not user_email:
        raise HTTPException(status_code=401, detail="Missing user email cookie")

    logs = (
        db.query(TableOrderLog)
        .filter(TableOrderLog.user_email == user_email)
        .order_by(TableOrderLog.created_at.desc())
        .all()
    )

    if not logs:
        raise HTTPException(status_code=404, detail="No order logs found for this user")

    responses = []
    for log in logs:
        responses.append(
            OrderResponse(
                order_id=log.order_id,
                status=log.status.value,
                created_at=log.created_at,
                estimated_delivery=log.estimated_delivery,
                tile_image=log.tile_image,
                tile_category=log.tile_category,
                tile_type=log.tile_type,
                tile_name=log.tile_name,
                tile_price=log.tile_price,
                quantity=log.quantity,
                total_price=log.tile_price * log.quantity,
                delivery_address=DeliveryAddress(
                    house_number=log.house_number,
                    street=log.street,
                    barangay=log.barangay,
                    city=log.city,
                    province=log.province,
                )
            )
        )

    return responses

# =========================
# ❌ Delete Order by ID
# =========================
@router.delete("/{order_id}")
def delete_order(order_id: int, user_email: str = Cookie(None), db: Session = Depends(get_db)):
    if not user_email:
        raise HTTPException(status_code=401, detail="User not found")

    order = db.query(TableOrders).filter(TableOrders.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    db.query(OrderItem).filter(OrderItem.order_id == order.id).delete()
    db.delete(order)
    db.commit()

    # ✅ Log recent activity
    activity = RecentActivity(
        email=user_email,
        activity=f"Deleted order #{order_id}",
        created_at=datetime.now(tools.PH_TZ)
    )
    db.add(activity)
    db.commit()

    return {"message": f"Order {order_id} has been deleted successfully."}
