"""
repositories/report_repo.py
All database operations for LLM generated Reports.
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from database.models.report import Report
from database.schemas.report import ReportCreate, ReportScoreUpdate
from typing import Optional, List


def create_report(db: Session, data: ReportCreate) -> Report:
    report = Report(**data.model_dump())
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def get_report_by_id(db: Session, report_id: int) -> Optional[Report]:
    return db.query(Report).filter(Report.id == report_id).first()


def get_reports_for_product(
    db: Session,
    product_id: int,
    limit: int = 10
) -> List[Report]:
    return (
        db.query(Report)
        .filter(Report.product_id == product_id)
        .order_by(desc(Report.created_at))
        .limit(limit)
        .all()
    )


def get_latest_report(db: Session, product_id: int) -> Optional[Report]:
    return (
        db.query(Report)
        .filter(Report.product_id == product_id)
        .order_by(desc(Report.created_at))
        .first()
    )


def update_report_scores(
    db: Session,
    report_id: int,
    data: ReportScoreUpdate
) -> Optional[Report]:
    """Called after a business analyst rates the report."""
    report = get_report_by_id(db, report_id)
    if not report:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(report, field, value)
    db.commit()
    db.refresh(report)
    return report


def get_average_scores(db: Session) -> dict:
    """
    Returns mean Likert scores across all rated reports.
    Mirrors the user study in the paper where analysts gave
    4.3/5 accuracy, 4.1/5 clarity, 4.0/5 actionability.
    """
    result = db.query(
        func.avg(Report.clarity_score).label("avg_clarity"),
        func.avg(Report.accuracy_score).label("avg_accuracy"),
        func.avg(Report.action_score).label("avg_actionability"),
        func.count(Report.id).label("total_reports"),
    ).first()

    return {
        "avg_clarity":       round(result.avg_clarity or 0, 2),
        "avg_accuracy":      round(result.avg_accuracy or 0, 2),
        "avg_actionability": round(result.avg_actionability or 0, 2),
        "total_reports":     result.total_reports,
    }