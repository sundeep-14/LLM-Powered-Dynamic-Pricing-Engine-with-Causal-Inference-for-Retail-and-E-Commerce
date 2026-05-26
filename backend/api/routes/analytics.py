from fastapi import APIRouter, Depends, Query
from typing import Optional
from backend.core.dependencies import get_current_user_id
from backend.utils.helpers import utcnow_iso
 
router = APIRouter()
 
 
@router.get("/summary")
async def get_summary(user_id: str = Depends(get_current_user_id)):
    """High-level KPI summary — will pull from DB in feature/database."""
    return {
        "total_products": 0,
        "avg_price_change_pct": 0.0,
        "total_revenue_today": 0.0,
        "competitor_entries": 0,
        "generated_at": utcnow_iso(),
    }
 
 
@router.get("/price-history/{product_id}")
async def get_price_history(
    product_id: str,
    days: int = Query(default=30, ge=1, le=365),
    user_id: str = Depends(get_current_user_id),
):
    """Price history for a product over N days — stub for pipeline integration."""
    return {
        "product_id": product_id,
        "days": days,
        "history": [],
        "generated_at": utcnow_iso(),
    }
 
 
@router.get("/demand-forecast/{product_id}")
async def get_demand_forecast(
    product_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Demand forecast stub — will be powered by pipeline/optimization."""
    return {
        "product_id": product_id,
        "forecast": [],
        "confidence": None,
        "generated_at": utcnow_iso(),
    }
 
 
@router.get("/competitor-analysis/{product_id}")
async def get_competitor_analysis(
    product_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Competitor price analysis stub."""
    return {
        "product_id": product_id,
        "avg_competitor_price": None,
        "min_competitor_price": None,
        "max_competitor_price": None,
        "our_price_position": None,
        "generated_at": utcnow_iso(),
    }