from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import crud_establishments
from app.models import User
from app.schemas.establishments import EstablishmentCreate, EstablishmentUpdate, EstablishmentResponse

router = APIRouter()

@router.get("/", response_model=List[EstablishmentResponse])
def get_establishments(
    user_id: int = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    if user_id:
        return crud_establishments.get_establishments_by_user(db, user_id=user_id, skip=skip, limit=limit)
    return crud_establishments.get_establishments(db, skip=skip, limit=limit)

@router.get("/{establishment_id}", response_model=EstablishmentResponse)
def get_establishment(
    establishment_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    establishment = crud_establishments.get_establishment(db, establishment_id)
    if not establishment:
        raise HTTPException(status_code=404, detail="Establishment not found")
    return establishment

@router.post("/", response_model=EstablishmentResponse)
def create_establishment(
    establishment: EstablishmentCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    return crud_establishments.create_establishment(db, establishment)

@router.put("/{establishment_id}", response_model=EstablishmentResponse)
def update_establishment(
    establishment_id: int,
    establishment: EstablishmentUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    db_establishment = crud_establishments.update_establishment(db, establishment_id, establishment)
    if not db_establishment:
        raise HTTPException(status_code=404, detail="Establishment not found")
    return db_establishment

@router.delete("/{establishment_id}")
def delete_establishment(
    establishment_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    success = crud_establishments.delete_establishment(db, establishment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Establishment not found")
    return {"message": "Establishment deleted successfully"}