"""
repositories/product_repo.py
All database operations for Products.
"""

from sqlalchemy.orm import Session
from database.models.product import Product
from database.schemas.product import ProductCreate, ProductUpdate
from typing import Optional, List


def create_product(db: Session, data: ProductCreate) -> Product:
    product = Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
    return db.query(Product).filter(Product.id == product_id).first()


def get_product_by_sku(db: Session, sku: str) -> Optional[Product]:
    return db.query(Product).filter(Product.sku == sku).first()


def get_all_products(
    db: Session,
    active_only: bool = True,
    skip: int = 0,
    limit: int = 100
) -> List[Product]:
    query = db.query(Product)
    if active_only:
        query = query.filter(Product.is_active == True)
    return query.offset(skip).limit(limit).all()


def get_products_by_category(db: Session, category: str) -> List[Product]:
    return db.query(Product).filter(
        Product.category == category,
        Product.is_active == True
    ).all()


def update_product(
    db: Session,
    product_id: int,
    data: ProductUpdate
) -> Optional[Product]:
    product = get_product_by_id(db, product_id)
    if not product:
        return None
    # model_dump(exclude_unset=True) only returns fields that were actually sent
    # so we don't accidentally overwrite fields with None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product_id: int) -> bool:
    product = get_product_by_id(db, product_id)
    if not product:
        return False
    # Soft delete — mark inactive instead of removing the row
    # This preserves historical pricing data linked to this product
    product.is_active = False
    db.commit()
    return True