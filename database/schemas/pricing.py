"""
schemas/pricing.py
------------------
Pydantic schemas for Pricing records.
Two separate update schemas because:
- PricingCreate  → when Bayesian Optimization recommends a price
- PricingUpdate  → when manager overrides or actual demand comes in
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PricingCreate(BaseModel):
    product_id:          int
    recommended_price:   float
    final_price:         Optional[float] = None
    demand_forecast:     Optional[float] = None
    pricing_date:        datetime
    optimization_method: str = "bayesian"


class PricingUpdate(BaseModel):
    """Used when manager overrides price or actual demand is recorded."""
    final_price:    Optional[float] = None
    actual_demand:  Optional[float] = None
    revenue:        Optional[float] = None
    margin:         Optional[float] = None


class PricingResponse(BaseModel):
    id:                  int
    product_id:          int
    recommended_price:   float
    final_price:         Optional[float]
    demand_forecast:     Optional[float]
    actual_demand:       Optional[float]
    revenue:             Optional[float]
    margin:              Optional[float]
    pricing_date:        datetime
    optimization_method: str
    created_at:          datetime

    class Config:
        from_attributes = True