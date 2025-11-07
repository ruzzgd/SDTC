from fastapi import APIRouter, Depends, Response, HTTPException, Cookie
from sqlalchemy.orm import Session
from DatabaseConnector import get_db
from models.AdminModel import AdminLogin,ChangePasswordRequest,OrderAdminUpdate,OrderAdminResponse,ProductStockUpdate
from database.AdminTable import Admin,RecentActivity
from database.UserTable import User, UserStatus
from database.ProductTable import Orders as TableOrders, OrderItem,OrderStatus,OrderLog,Sales,Products,StockRecord
from datetime import datetime, date, timedelta
from sqlalchemy import func
import tools
router = APIRouter(prefix="/admin",tags=["admin"])

@router.post("/login")
def login_admin(admin: AdminLogin, response: Response, db: Session = Depends(get_db)):
    db_admin = db.query(Admin).filter(
        Admin.email == admin.email,
        Admin.password == admin.password
    ).first()

    if not db_admin:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    response.set_cookie(
        key="admin_email",
        value=db_admin.email,
        httponly=True,
        secure=False,
        samesite="lax"
    )

    return {"message": "Admin logged in successfully"}


@router.post("/logout")
def logout_admin(response: Response):
    response.delete_cookie(key="admin_email")
    return {"message": "Admin logged out successfully"}


@router.get("/me")
def get_admin_email(admin_email: str | None = Cookie(default=None)):
    if not admin_email:
        raise HTTPException(status_code=401, detail="Not logged in")
    return {"email": admin_email}


# -------------------------
# Change password endpoint
# -------------------------
@router.post("/change-password")
def change_admin_password(
    data: ChangePasswordRequest,
    admin_email: str | None = Cookie(default=None),
    db: Session = Depends(get_db)
):
    if not admin_email:
        raise HTTPException(status_code=401, detail="Not logged in")

    db_admin = db.query(Admin).filter(Admin.email == admin_email).first()
    if not db_admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    # Directly update password
    db_admin.password = data.new_password
    db.commit()

    return {"message": "Password changed successfully"}

@router.get("/users")
def get_all_users(admin_email: str | None = Cookie(default=None), db: Session = Depends(get_db)):
    if not admin_email:
        raise HTTPException(status_code=401, detail="Not logged in")

    users = db.query(User).all()

    result = []
    for user in users:
        active_addresses = [addr for addr in user.addresses if addr.is_active]
        result.append({
            "id": user.id,
            "email": user.email,
            "status": "Banned" if user.status == UserStatus.Banned else "Active",
            "deliveryLocation": ", ".join([
                f"{addr.house_number}, {addr.street}, {addr.barangay}, {addr.city}, {addr.province}"
                for addr in active_addresses
            ]) if active_addresses else "",
        })

    return {"users": result}

@router.post("/users/{user_id}/ban")
def ban_user(user_id: int, admin_email: str | None = Cookie(default=None), db: Session = Depends(get_db)):

    if not admin_email:
        raise HTTPException(status_code=401, detail="Not logged in")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.status == UserStatus.Banned:
        user.status = UserStatus.Active
        action = "unbanned"
    else:
        user.status = UserStatus.Banned
        action = "banned"

    db.commit()
    return {"message": f"User {action} successfully", "user_id": user.id, "status": user.status.value}



@router.get("/orders/all")
def get_all_orders(db: Session = Depends(get_db)):
    orders = db.query(TableOrders).all()
    result = []

    for order in orders:
        order_item = db.query(OrderItem).filter(OrderItem.order_id == order.id).first()
        if order_item:
            result.append({
                "order_id": order.id,
                "product_id": order_item.product_id,
                "customer_email": order.user_email,
                "tile_name": order_item.tile_name,
                "tile_price": order_item.tile_price,
                "quantity": order_item.quantity,
                "created_at": order.created_at,
                "status": order.status,
                "estimated_delivery": order.estimated_delivery,
            })
    return result

@router.put("/orders/update/{order_id}", response_model=OrderAdminResponse)
def admin_update_order(order_id: int, update_data: OrderAdminUpdate, db: Session = Depends(get_db)):
    # ✅ Find the order
    order = db.query(TableOrders).filter(TableOrders.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # ✅ Handle status updates
    if update_data.status == OrderStatus.Approved.value:
        if not update_data.estimated_delivery:
            raise HTTPException(
                status_code=400,
                detail="Estimated delivery is required when approving an order"
            )
        order.status = OrderStatus.Approved.value
        order.estimated_delivery = update_data.estimated_delivery

    elif update_data.status == OrderStatus.Shipped.value:
        order.status = OrderStatus.Shipped.value

        # ✅ For each item in the order, check and update stock
        for item in order.items:
            product = db.query(Products).filter(Products.id == item.product_id).first()
            if not product:
                raise HTTPException(status_code=404, detail=f"Product with ID {item.product_id} not found")

            # ✅ Check stock availability
            if product.tile_stock < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Not enough stock for product '{product.tile_name}'. Available: {product.tile_stock}, Required: {item.quantity}"
                )

            # ✅ Reduce stock
            product.tile_stock -= item.quantity

            # ✅ Log the shipped item
            log = OrderLog(
                order_id=order.id,
                user_email=order.user_email,
                created_at=order.created_at,
                status=order.status,
                estimated_delivery=order.estimated_delivery,
                house_number=order.house_number,
                street=order.street,
                barangay=order.barangay,
                city=order.city,
                province=order.province,
                product_id=item.product_id,
                tile_name=item.tile_name,
                tile_category=item.tile_category,
                tile_type=item.tile_type,
                tile_image=item.tile_image,
                tile_price=item.tile_price,
                quantity=item.quantity
            )
            db.add(log)

            # ✅ Record sale
            sale = Sales(
                order_id=order.id,
                product_id=item.product_id,
                customer_email=order.user_email,
                tile_name=item.tile_name,
                tile_price=item.tile_price,
                quantity=item.quantity,
                total_price=item.tile_price * item.quantity
            )
            db.add(sale)

    elif update_data.status == OrderStatus.Rejected.value:
        order.status = OrderStatus.Rejected.value
        # ✅ Log rejection
        for item in order.items:
            log = OrderLog(
                order_id=order.id,
                user_email=order.user_email,
                created_at=order.created_at,
                status=order.status,
                estimated_delivery=order.estimated_delivery,
                house_number=order.house_number,
                street=order.street,
                barangay=order.barangay,
                city=order.city,
                province=order.province,
                product_id=item.product_id,
                tile_name=item.tile_name,
                tile_category=item.tile_category,
                tile_type=item.tile_type,
                tile_image=item.tile_image,
                tile_price=item.tile_price,
                quantity=item.quantity
            )
            db.add(log)

    else:
        raise HTTPException(status_code=400, detail="Invalid order status")

    # ✅ Commit all database changes
    db.commit()
    db.refresh(order)

    # ✅ Return updated order details
    order_item = db.query(OrderItem).filter(OrderItem.order_id == order.id).first()
    return OrderAdminResponse(
        order_id=order.id,
        product_id=order_item.product_id,
        customer_email=order.user_email,
        status=order.status,
        created_at=order.created_at,
        estimated_delivery=order.estimated_delivery,
        tile_name=order_item.tile_name,
        tile_price=order_item.tile_price,
        quantity=order_item.quantity,
    )


@router.delete("/orders/delete/{order_id}")
def admin_delete_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(TableOrders).filter(TableOrders.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # ✅ Log all order items before deleting
    for item in order.items:
        log = OrderLog(
            order_id=order.id,
            user_email=order.user_email,
            created_at=order.created_at,
            status=OrderStatus.Rejected, 
            estimated_delivery=order.estimated_delivery,
            house_number=order.house_number,
            street=order.street,
            barangay=order.barangay,
            city=order.city,
            province=order.province,
            product_id=item.product_id,
            tile_name=item.tile_name,
            tile_category=item.tile_category,
            tile_type=item.tile_type,
            tile_image=item.tile_image,
            tile_price=item.tile_price,
            quantity=item.quantity
        )
        db.add(log)

    # Delete order items first
    db.query(OrderItem).filter(OrderItem.order_id == order_id).delete()
    db.delete(order)
    db.commit()

    return {"message": f"Order {order_id} deleted successfully"}


# =========================
# 📜 Get all order logs
# =========================
@router.get("/orderlogs")
def get_order_logs(db: Session = Depends(get_db)):
    logs = db.query(OrderLog).all()

    response = []
    for log in logs:
        response.append({
            "order_id": log.order_id,
            "customer": log.user_email,
            "item_name": log.tile_name,
            "item_price": log.tile_price,
            "quantity": log.quantity,
            "total_price": log.tile_price * log.quantity,
            "date_ordered": log.created_at,
            "status": log.status,
        })

    return {"order_logs": response}

@router.put("/product/{product_id}/update-stock")
def update_product_stock(product_id: int, data: ProductStockUpdate, db: Session = Depends(get_db)):
    product = db.query(Products).filter(Products.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    previous_stock = product.tile_stock
    product.tile_stock = data.tile_stock

    # Create stock record
    record = StockRecord(
        product_id=product.id,
        change_type="update",
        previous_stock=previous_stock,
        new_stock=product.tile_stock,
        quantity_changed=data.tile_stock - previous_stock,
    )

    db.add(record)
    db.commit()
    db.refresh(product)

    return {
        "message": f"Stock updated to {data.tile_stock}",
        "product_id": product.id,
        "previous_stock": previous_stock,
        "new_stock": product.tile_stock
    }


@router.put("/product/{product_id}/add-stock")
def add_product_stock(product_id: int, data: ProductStockUpdate, db: Session = Depends(get_db)):
    product = db.query(Products).filter(Products.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    previous_stock = product.tile_stock
    product.tile_stock += data.tile_stock

    # Create stock record
    record = StockRecord(
        product_id=product.id,
        change_type="add",
        previous_stock=previous_stock,
        new_stock=product.tile_stock,
        quantity_changed=data.tile_stock,
    )

    db.add(record)
    db.commit()
    db.refresh(product)

    return {
        "message": f"Added {data.tile_stock} to stock",
        "product_id": product.id,
        "previous_stock": previous_stock,
        "new_stock": product.tile_stock
    }

@router.get("/product/stock-records")
def get_all_stock_records(db: Session = Depends(get_db)):
    # Fetch all stock records, newest first
    records = (
        db.query(StockRecord)
        .join(Products, StockRecord.product_id == Products.id)
        .order_by(StockRecord.created_at.desc())
        .all()
    )

    # If no records found
    if not records:
        return {"message": "No stock records found", "records": []}

    # Format the response
    return {
        "total_records": len(records),
        "records": [
            {
                "id": r.id,
                "product_id": r.product_id,
                "tile_name": r.product.tile_name if r.product else None,
                "tile_category": r.product.tile_category if r.product else None,
                "tile_type": r.product.tile_type if r.product else None,
                "change_type": r.change_type,
                "quantity_changed": r.quantity_changed,
                "previous_stock": r.previous_stock,
                "new_stock": r.new_stock,
                "created_at": r.created_at,
            }
            for r in records
        ],
    }

@router.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Return today's sales, orders, items sold, total sales, and low stock.
    Used for dashboard only.
    """
    today = date.today()
    tomorrow = today + timedelta(days=1)

    # Sales today
    total_sales_today = (
        db.query(func.sum(Sales.total_price))
        .filter(Sales.created_at >= today)
        .filter(Sales.created_at < tomorrow)
        .scalar()
        or 0
    )

    # Orders today
    total_orders_today = (
        db.query(TableOrders)
        .filter(TableOrders.created_at >= today)
        .filter(TableOrders.created_at < tomorrow)
        .count()
    )

    # Items sold today
    total_items_today = (
        db.query(func.sum(Sales.quantity))
        .filter(Sales.created_at >= today)
        .filter(Sales.created_at < tomorrow)
        .scalar()
        or 0
    )

    # Low stock count
    from database.ProductTable import Products
    low_stock_count = db.query(Products).filter(Products.tile_stock < 10).count()

    # Total sales overall
    total_sales_overall = db.query(func.sum(Sales.total_price)).scalar() or 0

    return {
        "total_sales_today": total_sales_today,
        "total_orders_today": total_orders_today,
        "total_items_today": total_items_today,
        "low_stock_count": low_stock_count,
        "total_sales_overall": total_sales_overall
    }

# Weekly sales performance for chart
@router.get("/sales/performance")
def get_sales_performance(db: Session = Depends(get_db)):
    today = date.today()
    dates = [today - timedelta(days=i) for i in reversed(range(7))]

    sales_data = []
    for d in dates:
        next_day = d + timedelta(days=1)
        daily_total = db.query(func.sum(Sales.total_price))\
            .filter(Sales.created_at >= d)\
            .filter(Sales.created_at < next_day)\
            .scalar() or 0
        sales_data.append(daily_total)

    categories = [d.strftime("%a") for d in dates]  # Mon, Tue, etc.
    return {"categories": categories, "data": sales_data}


@router.get("/customer_recent_activity", response_model=list[dict])
def get_recent_activities(admin_email: str = Cookie(None), db: Session = Depends(get_db)):
    if not admin_email:
        raise HTTPException(status_code=401, detail="Unauthorized access — Admin not found")

    one_day_ago = datetime.now(tools.PH_TZ) - timedelta(days=1)

    activities = (
        db.query(RecentActivity)
        .filter(RecentActivity.created_at >= one_day_ago)
        .order_by(RecentActivity.created_at.desc())
        .all()
    )

    return [
        {"activity": f"• {act.email} {act.activity} {act.created_at.strftime('%Y-%m-%d %H:%M:%S')}"}
        for act in activities
    ]


@router.get("/sales/report")
def generate_sales_report(
    start_date: date,
    end_date: date,
    admin_email: str | None = Cookie(default=None),
    db: Session = Depends(get_db)
):
    """
    Generate a summarized sales report for the selected date range only.
    Does NOT include 'today' data.
    """

    if not admin_email:
        raise HTTPException(status_code=401, detail="Not logged in")

    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date cannot be after end date")

    # 📊 Total sales in range
    total_sales = (
        db.query(func.sum(Sales.total_price))
        .filter(Sales.created_at >= start_date)
        .filter(Sales.created_at < end_date + timedelta(days=1))
        .scalar()
        or 0
    )

    # 🧾 Total orders in range
    total_orders = (
        db.query(TableOrders)
        .filter(TableOrders.created_at >= start_date)
        .filter(TableOrders.created_at < end_date + timedelta(days=1))
        .count()
    )

    # 📦 Total items sold in range
    total_items = (
        db.query(func.sum(Sales.quantity))
        .filter(Sales.created_at >= start_date)
        .filter(Sales.created_at < end_date + timedelta(days=1))
        .scalar()
        or 0
    )

    # 🏆 Best-selling products with total revenue
    best_sellers = (
        db.query(
            Sales.tile_name,
            func.sum(Sales.quantity).label("total_sold"),
            func.sum(Sales.total_price).label("total_revenue")
        )
        .filter(Sales.created_at >= start_date)
        .filter(Sales.created_at < end_date + timedelta(days=1))
        .group_by(Sales.tile_name)
        .order_by(func.sum(Sales.quantity).desc())
        .limit(5)
        .all()
    )

    return {
        "start_date": start_date,
        "end_date": end_date,
        "total_sales": total_sales,
        "total_orders": total_orders,
        "total_items": total_items,
        "best_sellers": [
            {
                "tile_name": name,
                "total_sold": sold,
                "total_revenue": revenue or 0
            }
            for name, sold, revenue in best_sellers
        ],
    }
