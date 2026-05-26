"""
pricing.py
----------
Records every price decision the engine makes.
This is your audit trail — you can always look back and see:
- What price did the system recommend?
- What price did the manager actually apply?
- What was the actual demand and revenue?
"""

from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from database.session import Base


class Pricing(Base):
    __tablename__ = "pricing"

    id                  = Column(Integer, primary_key=True, index=True)
    product_id          = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    recommended_price   = Column(Float, nullable=False)  # price Bayesian Optimization suggested
    final_price         = Column(Float, nullable=True)   # price actually applied (manager may override)
    demand_forecast     = Column(Float, nullable=True)   # DML model's demand estimate
    actual_demand       = Column(Float, nullable=True)   # real units sold (filled after the fact)
    revenue             = Column(Float, nullable=True)   # final_price × actual_demand
    margin              = Column(Float, nullable=True)   # (final_price - cost) × actual_demand
    pricing_date        = Column(DateTime, nullable=False)
    optimization_method = Column(String(50), default="bayesian")  # bayesian, rule_based, manual
    created_at          = Column(DateTime, server_default=func.now())

    product = relationship("Product", back_populates="pricing_records")