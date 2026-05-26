"""
causal_result.py
----------------
Stores output of the Causal Inference Engine (DoWhy + EconML).
One row per product per run.

The most important field is price_elasticity — this is θ (theta)
from the Double ML equation in the paper:
    D̃ = θP̃ + ε
It tells us: for every $1 increase in price, demand changes by θ units.
"""

from sqlalchemy import Column, Integer, Float, String, JSON, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from database.session import Base


class CausalResult(Base):
    __tablename__ = "causal_results"

    id                  = Column(Integer, primary_key=True, index=True)
    product_id          = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    price_elasticity    = Column(Float, nullable=False)   # θ from DML
    elasticity_ci_lower = Column(Float, nullable=True)    # confidence interval lower bound
    elasticity_ci_upper = Column(Float, nullable=True)    # confidence interval upper bound
    confounders_used    = Column(JSON, nullable=True)     # list of confounder column names
    feature_importances = Column(JSON, nullable=True)     # EconML attributions {feature: importance}
    refutation_passed   = Column(String(10), default="unknown")  # "yes", "no", "unknown"
    model_version       = Column(String(50), nullable=True)
    run_at              = Column(DateTime, server_default=func.now())

    product = relationship("Product", back_populates="causal_results")