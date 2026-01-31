from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Establishment, Report
from app.schemas.reports import ReportCreate, ReportUpdate


def get_report(db: Session, report_id: int) -> Optional[Report]:
    return db.query(Report).filter(Report.reporte_id == report_id).first()


def get_reports(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    establecimiento_id: Optional[int] = None,
) -> List[Report]:
    query = db.query(Report)
    if establecimiento_id is not None:
        query = query.filter(Report.establecimiento_id == establecimiento_id)
    return query.offset(skip).limit(limit).all()


def create_report(db: Session, report: ReportCreate) -> Report:
    # Verify establecimiento_id exists
    establishment = (
        db.query(Establishment)
        .filter(Establishment.establecimiento_id == report.establecimiento_id)
        .first()
    )
    if not establishment:
        raise ValueError(f"Establishment with id {report.establecimiento_id} does not exist")
    
    report_data = report.model_dump()
    db_report = Report(**report_data)  # type: ignore[arg-type]
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


def update_report(db: Session, report_id: int, report: ReportUpdate) -> Optional[Report]:
    db_report = get_report(db, report_id)
    if not db_report:
        return None

    update_data = report.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_report, field, value)

    db.commit()
    db.refresh(db_report)
    return db_report


def delete_report(db: Session, report_id: int) -> bool:
    db_report = get_report(db, report_id)
    if not db_report:
        return False

    db.delete(db_report)
    db.commit()
    return True
