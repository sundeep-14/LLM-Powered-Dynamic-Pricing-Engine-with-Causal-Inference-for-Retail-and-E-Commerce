from fastapi import APIRouter, Depends
from typing import Optional
from pydantic import BaseModel, Field
from backend.services.product_service import product_service
from backend.core.dependencies import get_current_user_id
 
router = APIRouter()
 
 
class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1)
    sku: str = Field(..., min_length=1)
    category: Optional[str] = ""
    base_price: float = Field(..., gt=0)
    stock: Optional[int] = 0
 
 
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    base_price: Optional[float] = None
    current_price: Optional[float] = None
    stock: Optional[int] = None
    is_active: Optional[bool] = None
 
 
@router.post("", status_code=201)
async def create_product(
    body: ProductCreate,
    user_id: str = Depends(get_current_user_id),
):
    return await product_service.create(body.model_dump(), created_by=user_id)
 
 
@router.get("")
async def list_products(
    skip: int = 0,
    limit: int = 20,
    user_id: str = Depends(get_current_user_id),
):
    return await product_service.get_all(skip=skip, limit=limit)
 
 
@router.get("/{product_id}")
async def get_product(
    product_id: str,
    user_id: str = Depends(get_current_user_id),
):
    return await product_service.get_by_id(product_id)
 
 
@router.patch("/{product_id}")
async def update_product(
    product_id: str,
    body: ProductUpdate,
    user_id: str = Depends(get_current_user_id),
):
    return await product_service.update(product_id, body.model_dump())
 
 
@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: str,
    user_id: str = Depends(get_current_user_id),
):
    await product_service.delete(product_id)