"""
schemas/report.py
-----------------
Pydantic schemas for LLM generated Reports.
ReportScoreUpdate is used when business analysts
rate the report in the user study (from the paper).
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ReportCreate(BaseModel):
    product_id:    int
    pricing_id:    Optional[int] = None
    generated_by:  Optional[int] = None
    llm_model:     Optional[str] = None
    report_text:   str


class ReportScoreUpdate(BaseModel):
    """Used when a business analyst rates the report 1-5."""
    clarity_score:  Optional[float] = None
    accuracy_score: Optional[float] = None
    action_score:   Optional[float] = None


class ReportResponse(BaseModel):
    id:             int
    product_id:     int
    pricing_id:     Optional[int]
    llm_model:      Optional[str]
    report_text:    str
    clarity_score:  Optional[float]
    accuracy_score: Optional[float]
    action_score:   Optional[float]
    created_at:     datetime

    class Config:
        from_attributes = True