from fastapi import APIRouter, Depends
from typing import Optional
from pydantic import BaseModel, Field
from backend.services.pricing_service import pricing_service
from backend.core.dependencies import get_current_user_id

router = APIRouter()


class PricingRuleCreate(BaseModel):
    strategy: str = Field(default="fixed", pattern="^(fixed|dynamic|competitive|margin)$")
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    target_margin_pct: Optional[float] = None


class ApplyPriceRequest(BaseModel):
    price: float = Field(..., gt=0)


class OptimizeRequest(BaseModel):
    base_price: float = Field(..., gt=0)
    cost_price: float = Field(..., gt=0)
    current_demand: float = Field(..., gt=0)
    price_elasticity: float = Field(default=-1.5)
    competitor_avg_price: Optional[float] = None
    stock: Optional[int] = 100
    category: Optional[str] = "general"
    seasonal_factor: Optional[float] = 1.0
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_margin_pct: Optional[float] = 10.0


@router.get("/{product_id}/current")
async def get_current_price(
    product_id: str,
    user_id: str = Depends(get_current_user_id),
):
    return await pricing_service.get_current_price(product_id)


@router.post("/{product_id}/optimize")
async def optimize_price(
    product_id: str,
    body: OptimizeRequest,
    user_id: str = Depends(get_current_user_id),
):
    """Run Bayesian optimization to find the profit-maximizing price."""
    return await pricing_service.optimize_price(product_id, body.model_dump())


@router.post("/{product_id}/rule", status_code=201)
async def set_pricing_rule(
    product_id: str,
    body: PricingRuleCreate,
    user_id: str = Depends(get_current_user_id),
):
    return await pricing_service.set_pricing_rule(product_id, body.model_dump(), user_id)


@router.get("/{product_id}/rule")
async def get_pricing_rule(
    product_id: str,
    user_id: str = Depends(get_current_user_id),
):
    return await pricing_service.get_pricing_rule(product_id)


@router.post("/{product_id}/apply")
async def apply_price(
    product_id: str,
    body: ApplyPriceRequest,
    user_id: str = Depends(get_current_user_id),
):
    return await pricing_service.apply_price(product_id, body.price, user_id)


@router.get("/{product_id}/history")
async def get_pricing_history(
    product_id: str,
    user_id: str = Depends(get_current_user_id),
):
    return await pricing_service.get_pricing_history(product_id)