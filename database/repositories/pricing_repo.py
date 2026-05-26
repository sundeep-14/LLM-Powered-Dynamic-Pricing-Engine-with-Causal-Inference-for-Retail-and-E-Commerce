"""
repositories/pricing_repo.py
All database operations for Pricing records.
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from database.models.pricing import Pricing
from database.schemas.pricing import PricingCreate, PricingUpdate
from typing import Optional, List
from datetime import datetime


def create_pricing_record(db: Session, data: PricingCreate) -> Pricing:
    pricing = Pricing(**data.model_dump())
    db.add(pricing)
    db.commit()
    db.refresh(pricing)
    return pricing


def get_pricing_by_id(db: Session, pricing_id: int) -> Optional[Pricing]:
    return db.query(Pricing).filter(Pricing.id == pricing_id).first()


def get_latest_price_for_product(db: Session, product_id: int) -> Optional[Pricing]:
    """Returns the most recent pricing record for a product."""
    return (
        db.query(Pricing)
        .filter(Pricing.product_id == product_id)
        .order_by(desc(Pricing.pricing_date))
        .first()
    )


def get_pricing_history(
    db: Session,
    product_id: int,
    limit: int = 30
) -> List[Pricing]:
    """Last N pricing records for a product, newest first."""
    return (
        db.query(Pricing)
        .filter(Pricing.product_id == product_id)
        .order_by(desc(Pricing.pricing_date))
        .limit(limit)
        .all()
    )


def get_pricing_by_date_range(
    db: Session,
    product_id: int,
    start: datetime,
    end: datetime
) -> List[Pricing]:
    """Fetch pricing records between two dates — useful for reports."""
    return (
        db.query(Pricing)
        .filter(
            Pricing.product_id == product_id,
            Pricing.pricing_date >= start,
            Pricing.pricing_date <= end,
        )
        .order_by(Pricing.pricing_date)
        .all()
    )


def update_pricing_record(
    db: Session,
    pricing_id: int,
    data: PricingUpdate
) -> Optional[Pricing]:
    """Used to fill in actual_demand and revenue after the fact."""
    pricing = get_pricing_by_id(db, pricing_id)
    if not pricing:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(pricing, field, value)
    db.commit()
    db.refresh(pricing)
    return pricing


def calculate_revenue_uplift(
    db: Session,
    product_id: int,
    baseline_price: float
) -> dict:
    """
    Compares revenue from LLM-DPECI prices vs naive baseline.
    This directly measures the 4.2% uplift mentioned in the paper.
    """
    records = db.query(Pricing).filter(
        Pricing.product_id == product_id,
        Pricing.actual_demand.isnot(None),
    ).all()

    if not records:
        return {"uplift_percent": 0.0, "record_count": 0}

    system_revenue = sum(r.revenue for r in records if r.revenue)
    naive_revenue  = sum(
        baseline_price * r.actual_demand
        for r in records if r.actual_demand
    )
    uplift = (
        (system_revenue - naive_revenue) / naive_revenue * 100
        if naive_revenue else 0.0
    )
    return {
        "uplift_percent": round(uplift, 2),
        "record_count": len(records)
    }