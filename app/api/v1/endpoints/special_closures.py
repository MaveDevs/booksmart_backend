from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.core.permissions import require_owner_or_admin, validate_establishment_access
from app.crud import crud_establishments, crud_special_closures
from app.models import User
from app.schemas.special_closures import SpecialClosureCreate, SpecialClosureResponse, SpecialClosureUpdate

router = APIRouter()


@router.get("/", response_model=List[SpecialClosureResponse])
def get_special_closures(
    establecimiento_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    return crud_special_closures.get_closures(db, skip=skip, limit=limit, establecimiento_id=establecimiento_id)


@router.post("/", response_model=SpecialClosureResponse)
def create_special_closure(
    closure: SpecialClosureCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_owner_or_admin()),
):
    establishment = crud_establishments.get_establishment(db, closure.establecimiento_id)
    if not establishment:
        raise HTTPException(status_code=404, detail="Establishment not found")

    validate_establishment_access(current_user, establishment)

    try:
        return crud_special_closures.create_closure(db, closure)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{closure_id}", response_model=SpecialClosureResponse)
def update_special_closure(
    closure_id: int,
    closure: SpecialClosureUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_owner_or_admin()),
):
    db_closure = crud_special_closures.get_closure(db, closure_id)
    if not db_closure:
        raise HTTPException(status_code=404, detail="Closure not found")

    establishment = crud_establishments.get_establishment(db, db_closure.establecimiento_id)
    if establishment:
        validate_establishment_access(current_user, establishment)

    updated = crud_special_closures.update_closure(db, closure_id, closure)
    return updated


@router.delete("/{closure_id}")
def delete_special_closure(
    closure_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_owner_or_admin()),
):
    db_closure = crud_special_closures.get_closure(db, closure_id)
    if not db_closure:
        raise HTTPException(status_code=404, detail="Closure not found")

    establishment = crud_establishments.get_establishment(db, db_closure.establecimiento_id)
    if establishment:
        validate_establishment_access(current_user, establishment)

    success = crud_special_closures.delete_closure(db, closure_id)
    if not success:
        raise HTTPException(status_code=404, detail="Closure not found")
    return {"message": "Closure deleted successfully"}