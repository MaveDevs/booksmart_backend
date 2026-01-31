from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import crud_agendas, crud_establishments
from app.models import User
from app.schemas.agendas import AgendaCreate, AgendaResponse, AgendaUpdate
from app.core.permissions import (
    require_owner_or_admin,
    validate_establishment_access,
)

router = APIRouter()


@router.get("/", response_model=List[AgendaResponse])
def get_agendas(
    establecimiento_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Any authenticated user can list agendas (read-only)."""
    return crud_agendas.get_agendas(db, skip=skip, limit=limit, establecimiento_id=establecimiento_id)


@router.get("/{agenda_id}", response_model=AgendaResponse)
def get_agenda(
    agenda_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Any authenticated user can view an agenda (read-only)."""
    agenda = crud_agendas.get_agenda(db, agenda_id)
    if not agenda:
        raise HTTPException(status_code=404, detail="Agenda not found")
    return agenda


@router.post("/", response_model=AgendaResponse)
def create_agenda(
    agenda: AgendaCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_owner_or_admin()),
):
    """Only owners and admins can create agendas. Owners can only create agendas for their own establishments."""
    # Verify establishment exists and user has access
    establishment = crud_establishments.get_establishment(db, agenda.establecimiento_id)
    if not establishment:
        raise HTTPException(status_code=404, detail="Establishment not found")
    
    # Owners can only create agendas for their own establishments
    validate_establishment_access(current_user, establishment)
    
    try:
        return crud_agendas.create_agenda(db, agenda)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{agenda_id}", response_model=AgendaResponse)
def update_agenda(
    agenda_id: int,
    agenda: AgendaUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_owner_or_admin()),
):
    """Only owners and admins can update agendas. Owners can only update agendas for their own establishments."""
    db_agenda = crud_agendas.get_agenda(db, agenda_id)
    if not db_agenda:
        raise HTTPException(status_code=404, detail="Agenda not found")
    
    # Verify user has access to the establishment this agenda belongs to
    establishment = crud_establishments.get_establishment(db, db_agenda.establecimiento_id)
    if establishment:
        validate_establishment_access(current_user, establishment)
    
    db_agenda = crud_agendas.update_agenda(db, agenda_id, agenda)
    return db_agenda


@router.patch("/{agenda_id}", response_model=AgendaResponse)
def patch_agenda(
    agenda_id: int,
    agenda: AgendaUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_owner_or_admin()),
):
    """Only owners and admins can patch agendas. Owners can only patch agendas for their own establishments."""
    db_agenda = crud_agendas.get_agenda(db, agenda_id)
    if not db_agenda:
        raise HTTPException(status_code=404, detail="Agenda not found")
    
    # Verify user has access to the establishment this agenda belongs to
    establishment = crud_establishments.get_establishment(db, db_agenda.establecimiento_id)
    if establishment:
        validate_establishment_access(current_user, establishment)
    
    db_agenda = crud_agendas.update_agenda(db, agenda_id, agenda)
    return db_agenda


@router.delete("/{agenda_id}")
def delete_agenda(
    agenda_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_owner_or_admin()),
):
    """Only owners and admins can delete agendas. Owners can only delete agendas for their own establishments."""
    db_agenda = crud_agendas.get_agenda(db, agenda_id)
    if not db_agenda:
        raise HTTPException(status_code=404, detail="Agenda not found")
    
    # Verify user has access to the establishment this agenda belongs to
    establishment = crud_establishments.get_establishment(db, db_agenda.establecimiento_id)
    if establishment:
        validate_establishment_access(current_user, establishment)
    
    success = crud_agendas.delete_agenda(db, agenda_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agenda not found")
    return {"message": "Agenda deleted successfully"}
