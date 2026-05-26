"""
init_db.py — Seed Script
-------------------------
Run this once after migrations to populate the DB with starter data.

Command: python -m database.init_db

What it inserts:
- 3 roles        (admin, analyst, manager)
- 1 admin user   (username: admin, password: Admin@1234)
- 3 products     (sample grocery items like Walmart M5 dataset)
"""

from database.session import SessionLocal, engine, Base
from database.models import *   # registers all models with Base
from database.models.role import Role
from database.repositories.user_repo import create_user, get_user_by_username
from database.repositories.product_repo import create_product, get_product_by_sku
from database.schemas.user import UserCreate
from database.schemas.product import ProductCreate


def seed_roles(db):
    """Insert default roles if they don't exist."""
    roles = [
        {"name": "admin",   "description": "Full system access"},
        {"name": "analyst", "description": "Can view causal results and reports"},
        {"name": "manager", "description": "Can approve and override prices"},
    ]
    for r in roles:
        exists = db.query(Role).filter(Role.name == r["name"]).first()
        if not exists:
            db.add(Role(**r))
    db.commit()
    print("Roles seeded")


def seed_admin_user(db):
    """Insert admin user if doesn't exist."""
    if not get_user_by_username(db, "admin"):
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        create_user(db, UserCreate(
            username="admin",
            email="admin@llm-dpeci.com",
            password="Admin@1234",
            role_id=admin_role.id,
        ))
        print("Admin user created")
        print("  username : admin")
        print("  password : Admin@1234")
    else:
        print("Admin user already exists, skipping")


def seed_products(db):
    """Insert sample products similar to Walmart M5 dataset."""
    sample_products = [
        ProductCreate(
            sku="DAIRY-001",
            name="Organic Whole Milk 1L",
            category="dairy",
            cost_price=1.20,
            base_price=2.49,
            min_price=1.50,
            max_price=3.99
        ),
        ProductCreate(
            sku="BAKERY-001",
            name="Sourdough Bread Loaf",
            category="bakery",
            cost_price=0.85,
            base_price=3.29,
            min_price=2.00,
            max_price=5.00
        ),
        ProductCreate(
            sku="DAIRY-002",
            name="Free Range Eggs 12 Pack",
            category="dairy",
            cost_price=1.80,
            base_price=4.99,
            min_price=3.00,
            max_price=7.50
        ),
    ]
    for p in sample_products:
        if not get_product_by_sku(db, p.sku):
            create_product(db, p)
    print("Sample products seeded")


if __name__ == "__main__":
    print("Starting database initialization...")
    print("")

    db = SessionLocal()
    try:
        seed_roles(db)
        seed_admin_user(db)
        seed_products(db)
        print("")
        print("Database initialized successfully!")
    finally:
        db.close()