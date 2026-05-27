from dataclasses import dataclass
from typing import Optional
from backend.utils.logger import logger


@dataclass
class PricingConstraints:
    """
    Hard and soft constraints that bound the optimizer's search space.
    All prices are in the same currency unit.
    """
    cost_price: float                    # hard floor — never price below cost
    min_price: Optional[float] = None    # business floor (e.g. MAP policy)
    max_price: Optional[float] = None    # business ceiling
    min_margin_pct: float = 5.0          # minimum margin in percent
    max_price_change_pct: float = 30.0   # max allowed change from current price
    current_price: Optional[float] = None

    def get_search_bounds(self) -> tuple[float, float]:
        """
        Returns (lower, upper) price bounds for the optimizer.
        Applies all constraints and returns the tightest valid range.
        """
        # Floor: cost + minimum margin
        margin_floor = self.cost_price * (1 + self.min_margin_pct / 100)
        lower = margin_floor

        if self.min_price is not None:
            lower = max(lower, self.min_price)

        # Ceiling: max_price or change-based ceiling
        if self.max_price is not None:
            upper = self.max_price
        elif self.current_price is not None:
            upper = self.current_price * (1 + self.max_price_change_pct / 100)
        else:
            upper = lower * 3.0  # fallback: 3x floor

        # Enforce lower < upper
        if lower >= upper:
            logger.warning(
                f"Constraint conflict: lower={lower:.2f} >= upper={upper:.2f}. "
                f"Widening upper bound."
            )
            upper = lower * 1.5

        logger.debug(f"Price search bounds: [{lower:.2f}, {upper:.2f}]")
        return lower, upper

    def is_valid_price(self, price: float) -> bool:
        lower, upper = self.get_search_bounds()
        return lower <= price <= upper

    def clamp(self, price: float) -> float:
        """Clamp a price to valid bounds."""
        lower, upper = self.get_search_bounds()
        return max(lower, min(upper, price))