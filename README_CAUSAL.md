# Data & Causal Inference Integration Guide
**For Member 3(Pratibha) — Data Collection & Causal Inference Engineer**

---

## Overview
This document explains how to read data from and write results to the
shared MySQL database built by Member 4 (Database Engineer).
You do NOT need to write any SQL — use the provided session and
repository functions.

---

## Step 1: Setup

### Install Dependencies
pip install sqlalchemy pymysql python-dotenv

### Start the Database
Make sure Docker is running, then:
docker-compose up -d

### Verify Connection
python -c "from database.session import engine; print('DB connected:', engine.url)"

---

## Step 2: Database Connection

Always use SessionLocal to get a database session:

from database.session import SessionLocal

db = SessionLocal()
try:
    # your code here
finally:
    db.close()   # always close when done

---

## Step 3: Reading Data for Your Pipeline

### Get All Active Products
Use this in data_loader.py to know which products to process:

from database.session import SessionLocal
from database.repositories.product_repo import get_all_products

db = SessionLocal()
products = get_all_products(db, active_only=True)

for product in products:
    print(product.id)          # product ID
    print(product.sku)         # e.g. "DAIRY-001"
    print(product.name)        # e.g. "Organic Whole Milk 1L"
    print(product.category)    # e.g. "dairy"
    print(product.cost_price)  # unit cost
    print(product.min_price)   # Bayesian Opt lower bound
    print(product.max_price)   # Bayesian Opt upper bound

db.close()

---

### Get Pricing History (Training Data for DML)
Use this in dml_estimator.py as your price-demand training data:

from database.session import SessionLocal
from database.repositories.pricing_repo import get_pricing_history

db = SessionLocal()

# get last 100 pricing records for product ID 1
records = get_pricing_history(db, product_id=1, limit=100)

for r in records:
    print(r.pricing_date)       # date of the price
    print(r.recommended_price)  # price the system set
    print(r.final_price)        # price manager applied
    print(r.actual_demand)      # real units sold
    print(r.revenue)            # revenue earned

db.close()

---

### Get Pricing by Date Range
Use this in feature_engineering.py to filter by time window:

from database.session import SessionLocal
from database.repositories.pricing_repo import get_pricing_by_date_range
from datetime import datetime

db = SessionLocal()

records = get_pricing_by_date_range(
    db,
    product_id=1,
    start=datetime(2025, 1, 1),
    end=datetime(2025, 12, 31)
)

db.close()

---

### Get Competitor Prices (Confounders)
Use this in confounders.py — competitor price is a key confounder
in the causal graph as described in the paper:

from database.session import SessionLocal
from database.models.competitor import Competitor

db = SessionLocal()

competitors = db.query(Competitor).filter(
    Competitor.product_id == 1
).all()

for c in competitors:
    print(c.competitor_name)   # e.g. "Walmart"
    print(c.competitor_price)  # their price
    print(c.captured_at)       # when it was scraped

db.close()

---

### Save Competitor Prices (Web Scraping Output)
Use this after scraping competitor prices to store them:

from database.session import SessionLocal
from database.models.competitor import Competitor
from datetime import datetime

db = SessionLocal()

competitor = Competitor(
    product_id=1,
    competitor_name="Walmart",
    competitor_price=2.29,
    source_url="https://walmart.com/...",
    captured_at=datetime.now()
)
db.add(competitor)
db.commit()

db.close()

---

## Step 4: Saving Causal Results

After running DoWhy + EconML, save results to causal_results table.
This is critical — the Bayesian Optimizer (Member 2) reads this table
to get price elasticities.

### Save DML Estimator Output
Use this in dml_estimator.py after running your causal model:

from database.session import SessionLocal
from database.models.causal_result import CausalResult
from datetime import datetime

db = SessionLocal()

result = CausalResult(
    product_id=1,

    # θ (theta) from the DML equation: D̃ = θP̃ + ε
    # negative means higher price = lower demand
    price_elasticity=-2.3,

    # confidence interval from EconML
    elasticity_ci_lower=-2.8,
    elasticity_ci_upper=-1.9,

    # list of confounders you used
    confounders_used=[
        "competitor_price",
        "seasonality",
        "weather_score",
        "event_proximity"
    ],

    # EconML feature attributions dict
    feature_importances={
        "competitor_price": 0.45,
        "seasonality": 0.30,
        "weather_score": 0.15,
        "event_proximity": 0.10
    },

    # did DoWhy refutation tests pass?
    refutation_passed="yes",   # "yes", "no", "unknown"

    model_version="dml_v1.0"
)

db.add(result)
db.commit()
db.refresh(result)

print("Causal result saved with ID:", result.id)
db.close()

---

## Step 5: Building Your Pandas DataFrame

Convert pricing records to a pandas DataFrame for your ML pipeline:

import pandas as pd
from database.session import SessionLocal
from database.repositories.pricing_repo import get_pricing_history
from database.models.competitor import Competitor

db = SessionLocal()

# --- Load pricing history ---
records = get_pricing_history(db, product_id=1, limit=500)

pricing_df = pd.DataFrame([{
    "date":           r.pricing_date,
    "price":          r.final_price or r.recommended_price,
    "demand":         r.actual_demand,
    "revenue":        r.revenue,
} for r in records])

# --- Load competitor prices ---
competitors = db.query(Competitor).filter(
    Competitor.product_id == 1
).all()

competitor_df = pd.DataFrame([{
    "date":              c.captured_at,
    "competitor_name":   c.competitor_name,
    "competitor_price":  c.competitor_price,
} for c in competitors])

# --- Merge for DML confounders DataFrame ---
merged_df = pd.merge_asof(
    pricing_df.sort_values("date"),
    competitor_df.sort_values("date"),
    on="date"
)

print(merged_df.head())
db.close()

---

## Step 6: Table Reference

These are the tables most relevant to your pipeline:

| Table | What it contains | You |
|---|---|---|
| products | product list with price bounds | READ |
| pricing | price + demand history | READ |
| competitor_pricing | scraped competitor prices | READ + WRITE |
| causal_results | your DML output | WRITE |
| activity_logs | audit trail | WRITE (optional) |

---

## Step 7: How Your Output Connects to Others

Your causal_results table is read by:
- Member 2 Backend → Bayesian Optimizer reads price_elasticity
- Member 2 Backend → RAG pipeline reads feature_importances
- Member 1 Frontend → Analytics.jsx displays elasticity charts

This is the exact flow from the paper:
DML estimates θ → Bayesian Optimizer uses θ → finds optimal price p*

---

## Database Connection Details

Host:      localhost
Port:      3307
Database:  llm_dpeci
User:      dpeci_user
Password:  dpeci_pass123
URL:       mysql+pymysql://dpeci_user:dpeci_pass123@localhost:3307/llm_dpeci

---

## Quick Reference — Most Used Imports

from database.session import SessionLocal
from database.models.product import Product
from database.models.pricing import Pricing
from database.models.competitor import Competitor
from database.models.causal_result import CausalResult
from database.repositories.product_repo import get_all_products
from database.repositories.pricing_repo import (
    get_pricing_history,
    get_pricing_by_date_range
)