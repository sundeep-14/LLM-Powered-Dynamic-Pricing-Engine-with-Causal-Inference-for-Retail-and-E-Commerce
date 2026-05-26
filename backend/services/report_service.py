from backend.utils.helpers import generate_uuid, utcnow_iso
from backend.utils.logger import logger

_reports: dict[str, dict] = {}


class ReportService:

    async def generate(self, report_type: str, params: dict, user_id: str) -> dict:
        """
        Generates a report entry.
        Will call pipeline/rag/report_generator.py in Week 4 (Commit 21).
        """
        report_id = generate_uuid()
        report = {
            "id": report_id,
            "type": report_type,
            "params": params,
            "status": "pending",
            "result": None,
            "requested_by": user_id,
            "created_at": utcnow_iso(),
            "completed_at": None,
        }
        _reports[report_id] = report
        logger.info(f"Report requested: type={report_type} id={report_id}")
        return report

    async def get_report(self, report_id: str) -> dict:
        from fastapi import HTTPException, status
        report = _reports.get(report_id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found",
            )
        return report

    async def list_reports(self, user_id: str) -> list:
        return [r for r in _reports.values() if r["requested_by"] == user_id]


report_service = ReportService()