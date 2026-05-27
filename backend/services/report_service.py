from backend.utils.helpers import generate_uuid, utcnow_iso
from backend.utils.logger import logger

_reports: dict[str, dict] = {}


class ReportService:

    async def generate(self, report_type: str, params: dict, user_id: str) -> dict:
        """
        Generates a report using RAG + LLM pipeline.
        """
        from backend.pipeline.rag.report_generator import report_generator
        from backend.pipeline.rag.knowledge_base import knowledge_base

        report_id = generate_uuid()
        product_id = params.get("product_id")

        logger.info(f"Generating report: type={report_type} product_id={product_id}")

        # Generate via LLM pipeline
        result = await report_generator.generate(
            report_type=report_type,
            product_id=product_id,
            extra_context=str(params) if params else None,
        )

        report = {
            "id": report_id,
            "type": report_type,
            "params": params,
            "status": result["status"],
            "content": result["content"],
            "context_used": result["context_used"],
            "requested_by": user_id,
            "created_at": utcnow_iso(),
            "completed_at": utcnow_iso(),
        }
        _reports[report_id] = report
        logger.info(f"Report completed: id={report_id} status={result['status']}")
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