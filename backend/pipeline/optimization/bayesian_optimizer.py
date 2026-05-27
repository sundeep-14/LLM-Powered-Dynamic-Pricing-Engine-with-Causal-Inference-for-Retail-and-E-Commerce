import numpy as np
from typing import Optional
from dataclasses import dataclass

from skopt import gp_minimize
from skopt.space import Real
from skopt.utils import use_named_args

from backend.pipeline.optimization.profit_function import ProfitFunction, ProductContext
from backend.pipeline.optimization.constraints import PricingConstraints
from backend.utils.logger import logger


@dataclass
class OptimizationResult:
    optimal_price: float
    expected_profit: float
    expected_demand: float
    expected_margin: float
    expected_margin_pct: float
    n_iterations: int
    search_bounds: tuple[float, float]
    convergence: str   # "converged" | "max_iterations" | "fallback"


class BayesianPriceOptimizer:
    """
    Uses Gaussian Process-based Bayesian Optimization (via scikit-optimize)
    to find the price that maximizes expected profit within constraints.

    Why Bayesian vs grid search:
    - Learns from each evaluation to focus on promising regions
    - Much fewer evaluations needed than brute-force
    - Handles noisy profit estimates well
    """

    def __init__(self, n_calls: int = 40, n_random_starts: int = 10, random_state: int = 42):
        self.n_calls = n_calls
        self.n_random_starts = n_random_starts
        self.random_state = random_state

    def optimize(
        self,
        context: ProductContext,
        constraints: PricingConstraints,
    ) -> OptimizationResult:
        """
        Run Bayesian optimization to find the profit-maximizing price.

        Args:
            context:     Product demand/cost/competitor data
            constraints: Price bounds and margin rules

        Returns:
            OptimizationResult with optimal price and supporting metrics
        """
        profit_fn = ProfitFunction(context)
        lower, upper = constraints.get_search_bounds()

        logger.info(
            f"Starting Bayesian optimization | "
            f"bounds=[{lower:.2f}, {upper:.2f}] | "
            f"n_calls={self.n_calls}"
        )

        search_space = [Real(lower, upper, name="price")]
        convergence = "converged"

        try:
            result = gp_minimize(
                func=profit_fn.negative_profit,
                dimensions=search_space,
                n_calls=self.n_calls,
                n_random_starts=self.n_random_starts,
                random_state=self.random_state,
                noise=1e-10,
                verbose=False,
            )
            optimal_price = float(result.x[0])
            optimal_price = constraints.clamp(optimal_price)

            if result.func_vals is not None:
                best_val = min(result.func_vals)
                if abs(best_val - result.fun) > 1.0:
                    convergence = "max_iterations"

        except Exception as e:
            logger.warning(f"Bayesian optimizer failed: {e}. Falling back to grid search.")
            optimal_price = self._grid_search_fallback(profit_fn, lower, upper)
            convergence = "fallback"

        # Build result metrics
        expected_profit = profit_fn.calculate_profit(optimal_price)
        expected_demand = profit_fn.estimate_demand(optimal_price)
        expected_margin = optimal_price - context.cost_price
        expected_margin_pct = (expected_margin / optimal_price * 100) if optimal_price > 0 else 0

        logger.info(
            f"Optimization complete | "
            f"optimal_price={optimal_price:.2f} | "
            f"profit={expected_profit:.2f} | "
            f"convergence={convergence}"
        )

        return OptimizationResult(
            optimal_price=round(optimal_price, 2),
            expected_profit=round(expected_profit, 2),
            expected_demand=round(expected_demand, 2),
            expected_margin=round(expected_margin, 2),
            expected_margin_pct=round(expected_margin_pct, 2),
            n_iterations=self.n_calls,
            search_bounds=(round(lower, 2), round(upper, 2)),
            convergence=convergence,
        )

    def _grid_search_fallback(
        self,
        profit_fn: ProfitFunction,
        lower: float,
        upper: float,
        steps: int = 100,
    ) -> float:
        """Simple grid search fallback if Bayesian optimizer errors out."""
        prices = np.linspace(lower, upper, steps)
        profits = [profit_fn.calculate_profit(p) for p in prices]
        best_idx = int(np.argmax(profits))
        return float(prices[best_idx])


# ── Convenience function for use in pricing_service ──────────────────────────

def run_optimization(
    product_id: str,
    base_price: float,
    cost_price: float,
    current_demand: float,
    price_elasticity: float = -1.5,
    competitor_avg_price: Optional[float] = None,
    stock: int = 100,
    category: str = "general",
    seasonal_factor: float = 1.0,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_margin_pct: float = 10.0,
) -> dict:
    """
    High-level entry point called by pricing_service.
    Returns a plain dict suitable for JSON serialization.
    """
    context = ProductContext(
        base_price=base_price,
        cost_price=cost_price,
        current_demand=current_demand,
        price_elasticity=price_elasticity,
        competitor_avg_price=competitor_avg_price or base_price,
        stock=stock,
        category=category,
        seasonal_factor=seasonal_factor,
    )

    constraints = PricingConstraints(
        cost_price=cost_price,
        min_price=min_price,
        max_price=max_price,
        min_margin_pct=min_margin_pct,
        current_price=base_price,
    )

    optimizer = BayesianPriceOptimizer()
    result = optimizer.optimize(context, constraints)

    return {
        "product_id": product_id,
        "optimal_price": result.optimal_price,
        "expected_profit": result.expected_profit,
        "expected_demand": result.expected_demand,
        "expected_margin": result.expected_margin,
        "expected_margin_pct": result.expected_margin_pct,
        "search_bounds": list(result.search_bounds),
        "n_iterations": result.n_iterations,
        "convergence": result.convergence,
    }