from fastapi import APIRouter, Depends
from typing import Optional
from pydantic import BaseModel
from backend.services.report_service import report_service
from backend.core.dependencies import get_current_user_id
 
router = APIRouter()
 
 
class ReportRequest(BaseModel):
    report_type: str = "pricing_summary"
    product_id: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
 
 
@router.post("", status_code=201)
async def request_report(
    body: ReportRequest,
    user_id: str = Depends(get_current_user_id),
):
    return await report_service.generate(
        report_type=body.report_type,
        params=body.model_dump(exclude={"report_type"}),
        user_id=user_id,
    )
 
 
@router.get("")
async def list_reports(user_id: str = Depends(get_current_user_id)):
    return await report_service.list_reports(user_id)
 
 
@router.get("/{report_id}")
async def get_report(
    report_id: str,
    user_id: str = Depends(get_current_user_id),
):
    return await report_service.get_report(report_id)