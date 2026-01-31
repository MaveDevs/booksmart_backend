from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import crud_plans
from app.models import User
from app.schemas.plans import PlanCreate, PlanResponse, PlanUpdate
from app.core.permissions import require_admin

router = APIRouter()


@router.get("/", response_model=List[PlanResponse])
def get_plans(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Any authenticated user can view plans (read-only)."""
    return crud_plans.get_plans(db, skip=skip, limit=limit)


@router.get("/{plan_id}", response_model=PlanResponse)
def get_plan(
    plan_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Any authenticated user can view a plan (read-only)."""
    plan = crud_plans.get_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@router.post("/", response_model=PlanResponse)
def create_plan(
    plan: PlanCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_admin()),
):
    """Only admins can create plans."""
    return crud_plans.create_plan(db, plan)


@router.put("/{plan_id}", response_model=PlanResponse)
def update_plan(
    plan_id: int,
    plan: PlanUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_admin()),
):
    """Only admins can update plans."""
    db_plan = crud_plans.update_plan(db, plan_id, plan)
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return db_plan


@router.patch("/{plan_id}", response_model=PlanResponse)
def patch_plan(
    plan_id: int,
    plan: PlanUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_admin()),
):
    """Only admins can patch plans."""
    db_plan = crud_plans.update_plan(db, plan_id, plan)
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return db_plan


@router.delete("/{plan_id}")
def delete_plan(
    plan_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_admin()),
):
    """Only admins can delete plans."""
    success = crud_plans.delete_plan(db, plan_id)
    if not success:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"message": "Plan deleted successfully"}
