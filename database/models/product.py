"""
product.py
----------
Each product is what the pricing engine optimizes prices for.
Contains price boundaries that the Bayesian Optimization module
uses as constraints — it won't recommend prices outside min/max range.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from database.session import Base


class Product(Base):
    __tablename__ = "products"

    id          = Column(Integer, primary_key=True, index=True)
    sku         = Column(String(100), unique=True, nullable=False, index=True)
    name        = Column(String(255), nullable=False)
    category    = Column(String(100), nullable=True)
    cost_price  = Column(Float, nullable=False)  # unit cost — used in profit calculation
    base_price  = Column(Float, nullable=False)  # default selling price
    min_price   = Column(Float, nullable=False)  # Bayesian Optimization lower bound
    max_price   = Column(Float, nullable=False)  # Bayesian Optimization upper bound
    is_active   = Column(Boolean, default=True)
    created_at  = Column(DateTime, server_default=func.now())
    updated_at  = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # One product links to many records in other tables
    pricing_records = relationship("Pricing", back_populates="product")
    competitor_data = relationship("Competitor", back_populates="product")
    causal_results  = relationship("CausalResult", back_populates="product")