from fastapi import APIRouter, Depends
from typing import Optional
from pydantic import BaseModel, Field
from backend.core.dependencies import get_current_user_id
from backend.utils.helpers import generate_uuid, utcnow_iso
 
router = APIRouter()
 
_competitors: dict[str, dict] = {}
 
 
class CompetitorCreate(BaseModel):
    name: str
    product_id: str
    price: float = Field(..., gt=0)
    url: Optional[str] = None
    source: Optional[str] = "manual"
 
 
@router.post("", status_code=201)
async def add_competitor_price(
    body: CompetitorCreate,
    user_id: str = Depends(get_current_user_id),
):
    entry = {
        "id": generate_uuid(),
        **body.model_dump(),
        "recorded_at": utcnow_iso(),
        "recorded_by": user_id,
    }
    _competitors[entry["id"]] = entry
    return entry
 
 
@router.get("")
async def list_competitor_prices(
    product_id: Optional[str] = None,
    user_id: str = Depends(get_current_user_id),
):
    items = list(_competitors.values())
    if product_id:
        items = [c for c in items if c["product_id"] == product_id]
    return items
 
 
@router.get("/{competitor_id}")
async def get_competitor_price(
    competitor_id: str,
    user_id: str = Depends(get_current_user_id),
):
    entry = _competitors.get(competitor_id)
    if not entry:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Competitor entry not found")
    return entry
 
 
@router.delete("/{competitor_id}", status_code=204)
async def delete_competitor_price(
    competitor_id: str,
    user_id: str = Depends(get_current_user_id),
):
    _competitors.pop(competitor_id, None)