"""
report.py
---------
Stores the LLM-generated pricing reports from the RAG pipeline.
The paper mentions business analysts rated reports on 3 dimensions:
- Factual accuracy
- Clarity  
- Actionability
All 3 scores are stored here for the user study evaluation.
"""

from sqlalchemy import Column, Integer, Float, Text, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from database.session import Base


class Report(Base):
    __tablename__ = "reports"

    id             = Column(Integer, primary_key=True, index=True)
    product_id     = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    pricing_id     = Column(Integer, ForeignKey("pricing.id"), nullable=True)
    generated_by   = Column(Integer, ForeignKey("users.id"), nullable=True)
    llm_model      = Column(String(50), nullable=True)   # "gpt-4", "claude-3", etc.
    report_text    = Column(Text, nullable=False)         # full natural language report
    clarity_score  = Column(Float, nullable=True)        # user study score 1-5
    accuracy_score = Column(Float, nullable=True)
    action_score   = Column(Float, nullable=True)
    created_at     = Column(DateTime, server_default=func.now())

    product      = relationship("Product")
    pricing      = relationship("Pricing")
    requested_by = relationship("User")