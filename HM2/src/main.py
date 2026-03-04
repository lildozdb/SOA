from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from generated_app.models import ProductCreate, ProductUpdate, ProductResponse, PageProductResponse, ProductStatus as DtoStatus

from src.database import get_db
from src.db_models import DBProduct, ProductStatus

app = FastAPI(title="Marketplace API with PostgreSQL")

@app.post("/products", response_model=ProductResponse, status_code=201)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = DBProduct(**product.model_dump(use_enum_values=True))
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/products/{id}", response_model=ProductResponse)
def get_product(id: UUID, db: Session = Depends(get_db)):
    db_product = db.query(DBProduct).filter(DBProduct.id == id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@app.get("/products", response_model=PageProductResponse)
def list_products(
    page: int = Query(0, ge=0),
    size: int = Query(20, ge=1),
    status: Optional[DtoStatus] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(DBProduct)
    
    if status:
        query = query.filter(DBProduct.status == status.value)
    if category:
        query = query.filter(DBProduct.category == category)
        
    total = query.count()
    items = query.offset(page * size).limit(size).all()
    
    return PageProductResponse(
        items=items,
        totalElements=total,
        page=page,
        size=size
    )

@app.put("/products/{id}", response_model=ProductResponse)
def update_product(id: UUID, product: ProductUpdate, db: Session = Depends(get_db)):
    db_product = db.query(DBProduct).filter(DBProduct.id == id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    update_data = product.model_dump(use_enum_values=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
        
    db.commit()
    db.refresh(db_product)
    return db_product

@app.delete("/products/{id}", status_code=204)
def delete_product(id: UUID, db: Session = Depends(get_db)):
    db_product = db.query(DBProduct).filter(DBProduct.id == id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    db_product.status = ProductStatus.ARCHIVED
    db.commit()
    return