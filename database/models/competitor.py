"""
competitor.py
-------------
Stores competitor price snapshots.
These are fed into the causal inference engine as confounders.
The paper mentions competitor pricing as one of the key variables
that affects demand — if we ignore it, our elasticity estimates
will be wrong.
"""

from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from database.session import Base


class Competitor(Base):
    __tablename__ = "competitor_pricing"

    id               = Column(Integer, primary_key=True, index=True)
    product_id       = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    competitor_name  = Column(String(150), nullable=False)
    competitor_price = Column(Float, nullable=False)
    source_url       = Column(String(500), nullable=True)  # where the price was scraped from
    captured_at      = Column(DateTime, nullable=False)    # when the snapshot was taken
    created_at       = Column(DateTime, server_default=func.now())

    product = relationship("Product", back_populates="competitor_data")