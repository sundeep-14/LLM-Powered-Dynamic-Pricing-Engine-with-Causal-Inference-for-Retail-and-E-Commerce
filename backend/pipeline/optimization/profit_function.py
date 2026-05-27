import numpy as np
from dataclasses import dataclass
from typing import Optional
from backend.utils.logger import logger


@dataclass
class ProductContext:
    """All the data needed to evaluate profit at a given price."""
    base_price: float
    cost_price: float
    current_demand: float          # units sold at current price
    price_elasticity: float        # how sensitive demand is to price change
    competitor_avg_price: float
    stock: int
    category: str = "general"
    seasonal_factor: float = 1.0   # >1 = high season, <1 = low season


class ProfitFunction:
    """
    Estimates expected profit at a given price point using:
    - Price elasticity demand model
    - Competitor price positioning
    - Seasonal adjustments
    - Stock constraints
    """

    def __init__(self, context: ProductContext):
        self.ctx = context

    def estimate_demand(self, price: float) -> float:
        """
        Demand model using price elasticity:
            Q(p) = Q0 * (p / p0) ^ elasticity * seasonal_factor
        Elasticity is negative (higher price → lower demand).
        Competitor adjustment: if our price < competitor, demand gets a boost.
        """
        ctx = self.ctx
        if ctx.base_price <= 0 or price <= 0:
            return 0.0

        # Base elasticity model
        price_ratio = price / ctx.base_price
        demand = ctx.current_demand * (price_ratio ** ctx.price_elasticity)

        # Competitor adjustment (±10% swing based on price position)
        if ctx.competitor_avg_price > 0:
            comp_ratio = ctx.competitor_avg_price / price
            competitor_factor = 1 + 0.1 * (comp_ratio - 1)
            competitor_factor = np.clip(competitor_factor, 0.85, 1.15)
            demand *= competitor_factor

        # Seasonal adjustment
        demand *= ctx.seasonal_factor

        # Cap at available stock
        demand = min(demand, ctx.stock)

        return max(0.0, demand)

    def calculate_profit(self, price: float) -> float:
        """
        Profit = (price - cost) * estimated_demand
        Returns negative profit for minimization-based optimizers.
        """
        if price <= self.ctx.cost_price:
            return 0.0

        demand = self.estimate_demand(price)
        margin = price - self.ctx.cost_price
        profit = margin * demand

        logger.debug(
            f"price={price:.2f} demand={demand:.2f} "
            f"margin={margin:.2f} profit={profit:.2f}"
        )
        return profit

    def negative_profit(self, price_list: list) -> float:
        """Wrapper for skopt minimizer (minimizes negative profit = maximizes profit)."""
        return -self.calculate_profit(price_list[0])