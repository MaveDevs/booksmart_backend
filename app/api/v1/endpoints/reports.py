from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import crud_reports, crud_establishments
from app.models import User
from app.schemas.reports import ReportCreate, ReportResponse, ReportUpdate
from app.core.permissions import (
    RoleType,
    get_user_role_name,
    require_admin,
    require_owner_or_admin,
)

router = APIRouter()


def _user_can_access_report(db: Session, user: User, report) -> bool:
    """Check if user can access this report."""
    user_role = get_user_role_name(user)
    
    # Admin can access all
    if user_role == RoleType.ADMIN.value:
        return True
    
    # Owner can only access reports for their establishments
    if user_role == RoleType.DUENO.value:
        establishment = crud_establishments.get_establishment(db, report.establecimiento_id)
        if establishment and establishment.usuario_id == user.usuario_id:
            return True
    
    return False


@router.get("/", response_model=List[ReportResponse])
def get_reports(
    establecimiento_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_owner_or_admin()),
):
    """
    List reports. Owners can only see reports for their establishments.
    Admins can see all reports.
    """
    user_role = get_user_role_name(current_user)
    
    # Admin can see all
    if user_role == RoleType.ADMIN.value:
        return crud_reports.get_reports(
            db, skip=skip, limit=limit, establecimiento_id=establecimiento_id
        )
    
    # Owner: filter by their establishments
    if establecimiento_id:
        establishment = crud_establishments.get_establishment(db, establecimiento_id)
        if not establishment or establishment.usuario_id != current_user.usuario_id:
            raise HTTPException(status_code=403, detail="You don't own this establishment")
        return crud_reports.get_reports(db, skip=skip, limit=limit, establecimiento_id=establecimiento_id)
    
    # Get reports for all owner's establishments
    establishments = crud_establishments.get_establishments_by_user(db, current_user.usuario_id)
    all_reports = []
    for est in establishments:
        reports = crud_reports.get_reports(db, establecimiento_id=est.establecimiento_id)
        all_reports.extend(reports)
    return all_reports[skip:skip + limit]


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_owner_or_admin()),
):
    """Get a specific report. Owners can only view reports for their establishments."""
    report = crud_reports.get_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if not _user_can_access_report(db, current_user, report):
        raise HTTPException(status_code=403, detail="You don't have access to this report")
    
    return report


@router.post("/", response_model=ReportResponse)
def create_report(
    report: ReportCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_admin()),
):
    """Only admins/system can create reports."""
    try:
        return crud_reports.create_report(db, report)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{report_id}", response_model=ReportResponse)
def update_report(
    report_id: int,
    report: ReportUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_admin()),
):
    """Only admins can update reports."""
    db_report = crud_reports.update_report(db, report_id, report)
    if not db_report:
        raise HTTPException(status_code=404, detail="Report not found")
    return db_report


@router.patch("/{report_id}", response_model=ReportResponse)
def patch_report(
    report_id: int,
    report: ReportUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_admin()),
):
    """Only admins can patch reports."""
    db_report = crud_reports.update_report(db, report_id, report)
    if not db_report:
        raise HTTPException(status_code=404, detail="Report not found")
    return db_report


@router.delete("/{report_id}")
def delete_report(
    report_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_admin()),
):
    """Only admins can delete reports."""
    success = crud_reports.delete_report(db, report_id)
    if not success:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"message": "Report deleted successfully"}
