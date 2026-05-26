"""
schemas/product.py
------------------
Pydantic schemas for Product.
Notice the Field() validator — it enforces business rules
like "cost price must be greater than 0"
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProductCreate(BaseModel):
    sku: str
    name: str
    category: Optional[str] = None
    cost_price: float = Field(..., gt=0, description="Must be greater than 0")
    base_price: float = Field(..., gt=0, description="Must be greater than 0")
    min_price:  float = Field(..., gt=0, description="Must be greater than 0")
    max_price:  float = Field(..., gt=0, description="Must be greater than 0")


class ProductUpdate(BaseModel):
    """All fields optional — only update what's provided."""
    name:       Optional[str]   = None
    category:   Optional[str]   = None
    cost_price: Optional[float] = None
    base_price: Optional[float] = None
    min_price:  Optional[float] = None
    max_price:  Optional[float] = None
    is_active:  Optional[bool]  = None


class ProductResponse(BaseModel):
    id:         int
    sku:        str
    name:       str
    category:   Optional[str]
    cost_price: float
    base_price: float
    min_price:  float
    max_price:  float
    is_active:  bool
    created_at: datetime

    class Config:
        from_attributes = True