from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import crud_services, crud_establishments
from app.models import User
from app.schemas.services import ServiceCreate, ServiceUpdate, ServiceResponse
from app.core.permissions import (
    require_owner_or_admin,
    validate_establishment_access,
    RoleType,
)

router = APIRouter()


@router.get("/", response_model=List[ServiceResponse])
def get_services(
    establishment_id: int = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Any authenticated user can list services (read-only)."""
    if establishment_id:
        return crud_services.get_services_by_establishment(db, establishment_id=establishment_id, skip=skip, limit=limit)
    return crud_services.get_services(db, skip=skip, limit=limit)


@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(
    service_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Any authenticated user can view a service (read-only)."""
    service = crud_services.get_service(db, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.post("/", response_model=ServiceResponse)
def create_service(
    service: ServiceCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_owner_or_admin()),
):
    """Only owners and admins can create services. Owners can only create services for their own establishments."""
    # Verify establishment exists and user has access
    establishment = crud_establishments.get_establishment(db, service.establecimiento_id)
    if not establishment:
        raise HTTPException(status_code=404, detail="Establishment not found")
    
    # Owners can only create services for their own establishments
    validate_establishment_access(current_user, establishment)
    
    try:
        return crud_services.create_service(db, service)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{service_id}", response_model=ServiceResponse)
def update_service(
    service_id: int,
    service: ServiceUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_owner_or_admin()),
):
    """Only owners and admins can update services. Owners can only update services for their own establishments."""
    db_service = crud_services.get_service(db, service_id)
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Verify user has access to the establishment this service belongs to
    establishment = crud_establishments.get_establishment(db, db_service.establecimiento_id)
    if establishment:
        validate_establishment_access(current_user, establishment)
    
    db_service = crud_services.update_service(db, service_id, service)
    return db_service


@router.patch("/{service_id}", response_model=ServiceResponse)
def patch_service(
    service_id: int,
    service: ServiceUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_owner_or_admin()),
):
    """Only owners and admins can patch services. Owners can only patch services for their own establishments."""
    db_service = crud_services.get_service(db, service_id)
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Verify user has access to the establishment this service belongs to
    establishment = crud_establishments.get_establishment(db, db_service.establecimiento_id)
    if establishment:
        validate_establishment_access(current_user, establishment)
    
    db_service = crud_services.update_service(db, service_id, service)
    return db_service


@router.delete("/{service_id}")
def delete_service(
    service_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_owner_or_admin()),
):
    """Only owners and admins can delete services. Owners can only delete services for their own establishments."""
    db_service = crud_services.get_service(db, service_id)
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Verify user has access to the establishment this service belongs to
    establishment = crud_establishments.get_establishment(db, db_service.establecimiento_id)
    if establishment:
        validate_establishment_access(current_user, establishment)
    
    success = crud_services.delete_service(db, service_id)
    if not success:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"message": "Service deleted successfully"}