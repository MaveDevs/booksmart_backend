from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import crud_services
from app.models import User
from app.schemas.services import ServiceCreate, ServiceUpdate, ServiceResponse

router = APIRouter()

@router.get("/", response_model=List[ServiceResponse])
def get_services(
    establishment_id: int = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    if establishment_id:
        return crud_services.get_services_by_establishment(db, establishment_id=establishment_id, skip=skip, limit=limit)
    return crud_services.get_services(db, skip=skip, limit=limit)

@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(
    service_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    service = crud_services.get_service(db, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@router.post("/", response_model=ServiceResponse)
def create_service(
    service: ServiceCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    return crud_services.create_service(db, service)

@router.put("/{service_id}", response_model=ServiceResponse)
def update_service(
    service_id: int,
    service: ServiceUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    db_service = crud_services.update_service(db, service_id, service)
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    return db_service

@router.delete("/{service_id}")
def delete_service(
    service_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    success = crud_services.delete_service(db, service_id)
    if not success:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"message": "Service deleted successfully"}