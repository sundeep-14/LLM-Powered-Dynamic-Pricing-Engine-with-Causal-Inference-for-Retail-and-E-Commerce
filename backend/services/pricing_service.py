from fastapi import HTTPException, status
from backend.utils.helpers import generate_uuid, utcnow_iso
from backend.utils.logger import logger

_pricing_rules: dict[str, dict] = {}
_pricing_history: list[dict] = []


class PricingService:

    async def get_current_price(self, product_id: str) -> dict:
        """
        Returns current price for a product.
        Will integrate with Bayesian optimizer (pipeline/optimization) in Week 3.
        """
        return {
            "product_id": product_id,
            "current_price": None,
            "recommended_price": None,
            "strategy": "pending_pipeline_integration",
            "generated_at": utcnow_iso(),
        }

    async def set_pricing_rule(self, product_id: str, data: dict, user_id: str) -> dict:
        rule_id = generate_uuid()
        rule = {
            "id": rule_id,
            "product_id": product_id,
            "strategy": data.get("strategy", "fixed"),
            "min_price": data.get("min_price"),
            "max_price": data.get("max_price"),
            "target_margin_pct": data.get("target_margin_pct"),
            "is_active": True,
            "created_by": user_id,
            "created_at": utcnow_iso(),
        }
        _pricing_rules[product_id] = rule
        logger.info(f"Pricing rule set for product_id={product_id} strategy={rule['strategy']}")
        return rule

    async def get_pricing_rule(self, product_id: str) -> dict:
        rule = _pricing_rules.get(product_id)
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No pricing rule found for this product",
            )
        return rule

    async def apply_price(self, product_id: str, price: float, user_id: str) -> dict:
        """
        Applies a price to a product and records it in history.
        Will write to DB in feature/database.
        """
        entry = {
            "id": generate_uuid(),
            "product_id": product_id,
            "applied_price": price,
            "applied_by": user_id,
            "applied_at": utcnow_iso(),
        }
        _pricing_history.append(entry)
        logger.info(f"Price applied: product_id={product_id} price={price}")
        return entry

    async def get_pricing_history(self, product_id: str) -> list:
        return [e for e in _pricing_history if e["product_id"] == product_id]


pricing_service = PricingService()