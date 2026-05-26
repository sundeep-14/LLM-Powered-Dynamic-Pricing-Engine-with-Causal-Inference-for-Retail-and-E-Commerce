# Backend Integration Guide
**For Member 2(Shivani) — Backend Developer**

---

## Overview
This document explains how to connect FastAPI routes and services
to the shared MySQL database built by Member 4 Sundeep(Database Engineer).
You do NOT need to write any SQL or touch the database directly.
Use the provided session, repositories, and schemas.

---

## Step 1: Setup

### Install Dependencies
pip install sqlalchemy pymysql python-dotenv fastapi uvicorn

### Start the Database
Make sure Docker is running, then:
docker-compose up -d

### Verify Connection
python -c "from database.session import engine; print('DB connected:', engine.url)"

---

## Step 2: Database Session in FastAPI

### The get_db Dependency
FastAPI uses dependency injection to give every route a DB session.
Always use get_db — never create a session manually in routes.

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.session import get_db

router = APIRouter()

@router.get("/example")
def example_route(db: Session = Depends(get_db)):
    # db is your database session
    # it automatically closes when the request is done
    pass

---

## Step 3: Authentication Routes
### File: backend/api/routes/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.session import get_db
from database.repositories.user_repo import (
    authenticate_user,
    create_user,
    get_user_by_username,
    get_user_by_email
)
from database.schemas.user import UserCreate, UserLogin, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=dict)
def register(data: UserCreate, db: Session = Depends(get_db)):
    # check if username already exists
    if get_user_by_username(db, data.username):
        raise HTTPException(status_code=400, detail="Username already taken")

    # check if email already exists
    if get_user_by_email(db, data.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    # create the user — password is hashed inside create_user
    user = create_user(db, data)
    return {"message": "User created", "user_id": user.id}


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    # authenticate_user checks username + password hash
    user = authenticate_user(db, data.username, data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # generate JWT token (your security.py handles this)
    access_token = create_access_token({"sub": user.username})
    return TokenResponse(access_token=access_token)

---

## Step 4: Product Routes
### File: backend/api/routes/products.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database.session import get_db
from database.repositories.product_repo import (
    get_all_products,
    get_product_by_id,
    get_product_by_sku,
    get_products_by_category,
    create_product,
    update_product,
    delete_product
)
from database.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse
)

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=List[ProductResponse])
def list_products(
    category: str = None,
    db: Session = Depends(get_db)
):
    if category:
        return get_products_by_category(db, category)
    return get_all_products(db)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/", response_model=ProductResponse)
def add_product(data: ProductCreate, db: Session = Depends(get_db)):
    # check SKU is unique
    if get_product_by_sku(db, data.sku):
        raise HTTPException(status_code=400, detail="SKU already exists")
    return create_product(db, data)


@router.put("/{product_id}", response_model=ProductResponse)
def edit_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db)
):
    product = update_product(db, product_id, data)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.delete("/{product_id}")
def remove_product(product_id: int, db: Session = Depends(get_db)):
    # soft delete — marks is_active=False, preserves history
    success = delete_product(db, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deactivated"}

---

## Step 5: Pricing Routes
### File: backend/api/routes/pricing.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database.session import get_db
from database.repositories.pricing_repo import (
    create_pricing_record,
    get_pricing_by_id,
    get_latest_price_for_product,
    get_pricing_history,
    update_pricing_record,
    calculate_revenue_uplift
)
from database.schemas.pricing import (
    PricingCreate,
    PricingUpdate,
    PricingResponse
)

router = APIRouter(prefix="/pricing", tags=["pricing"])


@router.get("/{product_id}/latest", response_model=PricingResponse)
def get_latest_price(product_id: int, db: Session = Depends(get_db)):
    pricing = get_latest_price_for_product(db, product_id)
    if not pricing:
        raise HTTPException(status_code=404, detail="No pricing record found")
    return pricing


@router.get("/{product_id}/history", response_model=List[PricingResponse])
def get_price_history(
    product_id: int,
    limit: int = 30,
    db: Session = Depends(get_db)
):
    return get_pricing_history(db, product_id, limit)


@router.post("/", response_model=PricingResponse)
def create_price(data: PricingCreate, db: Session = Depends(get_db)):
    # called by Bayesian Optimizer after finding optimal price
    return create_pricing_record(db, data)


@router.put("/{pricing_id}", response_model=PricingResponse)
def update_price(
    pricing_id: int,
    data: PricingUpdate,
    db: Session = Depends(get_db)
):
    # called when manager overrides price or actual demand comes in
    pricing = update_pricing_record(db, pricing_id, data)
    if not pricing:
        raise HTTPException(status_code=404, detail="Pricing record not found")
    return pricing


@router.get("/{product_id}/uplift")
def revenue_uplift(
    product_id: int,
    baseline_price: float,
    db: Session = Depends(get_db)
):
    # compares LLM-DPECI revenue vs naive baseline
    # directly measures the 4.2% uplift from the paper
    return calculate_revenue_uplift(db, product_id, baseline_price)

---

## Step 6: Reports Routes
### File: backend/api/routes/reports.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database.session import get_db
from database.repositories.report_repo import (
    create_report,
    get_report_by_id,
    get_reports_for_product,
    get_latest_report,
    update_report_scores,
    get_average_scores
)
from database.schemas.report import (
    ReportCreate,
    ReportScoreUpdate,
    ReportResponse
)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/scores/average")
def average_scores(db: Session = Depends(get_db)):
    # returns mean Likert scores from user study
    # paper reports: 4.3 accuracy, 4.1 clarity, 4.0 actionability
    return get_average_scores(db)


@router.get("/{product_id}/latest", response_model=ReportResponse)
def latest_report(product_id: int, db: Session = Depends(get_db)):
    report = get_latest_report(db, product_id)
    if not report:
        raise HTTPException(status_code=404, detail="No report found")
    return report


@router.get("/{product_id}/all", response_model=List[ReportResponse])
def all_reports(
    product_id: int,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    return get_reports_for_product(db, product_id, limit)


@router.post("/", response_model=ReportResponse)
def save_report(data: ReportCreate, db: Session = Depends(get_db)):
    # called by RAG pipeline after LLM generates report
    return create_report(db, data)


@router.put("/{report_id}/score")
def score_report(
    report_id: int,
    data: ReportScoreUpdate,
    db: Session = Depends(get_db)
):
    # called when business analyst rates the report (user study)
    report = update_report_scores(db, report_id, data)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"message": "Score updated", "report_id": report.id}

---

## Step 7: User & Admin Routes
### File: backend/api/routes/users.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database.session import get_db
from database.repositories.user_repo import (
    get_all_users,
    get_user_by_id,
    update_user,
    delete_user
)
from database.schemas.user import UserUpdate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return get_all_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def edit_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db)
):
    user = update_user(db, user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}")
def remove_user(user_id: int, db: Session = Depends(get_db)):
    success = delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}

---

## Step 8: Activity Logging
### File: backend/services/admin_service.py
Use this to log every important action for the audit trail:

from database.session import SessionLocal
from database.models.activity_log import ActivityLog

def log_action(
    db,
    user_id: int,
    action: str,
    entity_type: str = None,
    entity_id: int = None,
    detail: str = None
):
    log = ActivityLog(
        user_id=user_id,
        action=action,         # "PRICE_UPDATED", "REPORT_GENERATED"
        entity_type=entity_type, # "product", "pricing", "report"
        entity_id=entity_id,
        detail=detail
    )
    db.add(log)
    db.commit()

# Example usage in a route:
# log_action(db, user_id=1, action="PRICE_UPDATED",
#            entity_type="pricing", entity_id=5,
#            detail="Manager overrode price from 2.49 to 2.99")

---

## Step 9: Connecting the Pipeline

### Bayesian Optimizer saves to DB
### File: backend/pipeline/optimization/bayesian_optimizer.py

from database.session import SessionLocal
from database.repositories.pricing_repo import create_pricing_record
from database.schemas.pricing import PricingCreate
from datetime import datetime

def save_optimized_price(product_id: int, optimal_price: float, forecast: float):
    db = SessionLocal()
    try:
        record = create_pricing_record(db, PricingCreate(
            product_id=product_id,
            recommended_price=optimal_price,
            demand_forecast=forecast,
            pricing_date=datetime.now(),
            optimization_method="bayesian"
        ))
        return record.id
    finally:
        db.close()


### RAG Pipeline saves report to DB
### File: backend/pipeline/rag/report_generator.py

from database.session import SessionLocal
from database.repositories.report_repo import create_report
from database.schemas.report import ReportCreate

def save_generated_report(
    product_id: int,
    pricing_id: int,
    report_text: str,
    llm_model: str = "gpt-4"
):
    db = SessionLocal()
    try:
        report = create_report(db, ReportCreate(
            product_id=product_id,
            pricing_id=pricing_id,
            report_text=report_text,
            llm_model=llm_model
        ))
        return report.id
    finally:
        db.close()

---

## Step 10: Table Reference

| Table | Route | Operations |
|---|---|---|
| users | /auth /users | READ WRITE UPDATE DELETE |
| roles | /admin | READ |
| products | /products | READ WRITE UPDATE DELETE |
| pricing | /pricing | READ WRITE UPDATE |
| reports | /reports | READ WRITE UPDATE |
| causal_results | /analytics | READ |
| competitor_pricing | /competitors | READ WRITE |
| activity_logs | /admin | READ WRITE |

---

## Quick Reference — Most Used Imports

from database.session import get_db, SessionLocal
from database.repositories.user_repo import (
    create_user, get_user_by_id,
    get_user_by_username, authenticate_user,
    get_all_users, update_user, delete_user
)
from database.repositories.product_repo import (
    create_product, get_product_by_id,
    get_all_products, update_product, delete_product
)
from database.repositories.pricing_repo import (
    create_pricing_record, get_pricing_history,
    get_latest_price_for_product, update_pricing_record,
    calculate_revenue_uplift
)
from database.repositories.report_repo import (
    create_report, get_report_by_id,
    get_reports_for_product, update_report_scores,
    get_average_scores
)
from database.schemas.user import UserCreate, UserUpdate, UserResponse
from database.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from database.schemas.pricing import PricingCreate, PricingUpdate, PricingResponse
from database.schemas.report import ReportCreate, ReportScoreUpdate, ReportResponse

---

## Database Connection Details

Host:      localhost
Port:      3307
Database:  llm_dpeci
User:      dpeci_user
Password:  dpeci_pass123
URL:       mysql+pymysql://dpeci_user:dpeci_pass123@localhost:3307/llm_dpeci