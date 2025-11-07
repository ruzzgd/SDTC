from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from DatabaseConnector import get_db
from database.ProductTable import Products,Sales
from models.ProductModel import ProductResponse,AddNewProduct,UpdateProduct


router = APIRouter(prefix="/product",tags=["product"])


@router.get("/admin", response_model=list[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    products = db.query(Products).all()
    return products

@router.get("/", response_model=list[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    products = db.query(Products).filter(Products.is_archived == False).all()
    return products


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Products).filter(
        Products.id == product_id,
        Products.is_archived == False
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/add-product",response_model=ProductResponse)
def add_new_product(product_data:AddNewProduct, db: Session = Depends(get_db)):
    new_product = Products(
        tile_image=product_data.tile_image,
        tile_category=product_data.tile_category,
        tile_type=product_data.tile_type,
        tile_name=product_data.tile_name,
        tile_description=product_data.tile_description,
        tile_price=product_data.tile_price,
        tile_stock=product_data.tile_stock,
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product_data: UpdateProduct, db: Session = Depends(get_db)):
    db_product = db.query(Products).filter(Products.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    db_product.tile_image = product_data.tile_image
    db_product.tile_category = product_data.tile_category
    db_product.tile_type = product_data.tile_type
    db_product.tile_name = product_data.tile_name
    db_product.tile_description = product_data.tile_description
    db_product.tile_price = product_data.tile_price
    db_product.tile_stock = product_data.tile_stock

    db.commit()
    db.refresh(db_product)
    return db_product


@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(Products).filter(Products.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(db_product)
    db.commit()
    return {"message": f"Product {product_id} deleted successfully"}



@router.patch("/toggle-archive/{product_id}", response_model=ProductResponse)
def toggle_archive(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Products).filter(Products.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.is_archived = not product.is_archived

    db.commit()
    db.refresh(product)
    return product

@router.get("/sold/{product_id}")
def get_total_sold(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Products).filter(Products.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    total_sold = (
        db.query(func.sum(Sales.quantity))
        .filter(Sales.product_id == product_id)
        .scalar()
    ) or 0

    return {"product_id": product_id, "total_sold": total_sold}


