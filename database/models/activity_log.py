"""
activity_log.py
---------------
Audit log — records every important action in the system.
Examples:
    - User logged in
    - Price was updated
    - Report was generated
    - Causal model was run

As a DB engineer this table is very useful for debugging:
"Why did the price change on Monday?" → check activity_logs
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from database.session import Base


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=True)  # nullable for system actions
    action      = Column(String(100), nullable=False)  # "PRICE_UPDATED", "REPORT_GENERATED"
    entity_type = Column(String(50), nullable=True)    # "product", "report", "pricing"
    entity_id   = Column(Integer, nullable=True)       # ID of the affected record
    detail      = Column(Text, nullable=True)          # free text description
    created_at  = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="activity_logs")