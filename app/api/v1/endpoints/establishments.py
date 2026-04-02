from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.core.permissions import (
    require_owner_or_admin,
    validate_establishment_access,
    get_user_role_name,
    RoleType,
)
from app.crud import crud_establishments
from app.models import User
from app.schemas.establishments import (
    EstablishmentCreate,
    EstablishmentUpdate,
    EstablishmentResponse,
    NearbyEstablishmentResponse,
)

router = APIRouter()


@router.get("/", response_model=List[EstablishmentResponse])
def get_establishments(
    user_id: int = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Get all establishments (all authenticated users can read)"""
    if user_id:
        return crud_establishments.get_establishments_by_user(db, user_id=user_id, skip=skip, limit=limit)
    return crud_establishments.get_establishments(db, skip=skip, limit=limit)


@router.get("/nearby", response_model=list[NearbyEstablishmentResponse])
def get_nearby_establishments(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(10.0, gt=0, le=200),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Get nearby active establishments ranked by distance and subscription priority."""
    ranked_establishments = crud_establishments.get_establishments_nearby(
        db,
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        skip=skip,
        limit=limit,
    )

    return [
        NearbyEstablishmentResponse.model_validate(
            {
                **EstablishmentResponse.model_validate(item["establishment"], from_attributes=True).model_dump(),
                "distance_km": item["distance_km"],
                "ranking_score": item["ranking_score"],
                "subscription_active": item["subscription_active"],
                "subscription_plan_id": item["subscription_plan_id"],
                "subscription_plan_name": item["subscription_plan_name"],
            }
        )
        for item in ranked_establishments
    ]


@router.get("/{establishment_id}", response_model=EstablishmentResponse)
def get_establishment(
    establishment_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Get establishment by ID (all authenticated users can read)"""
    establishment = crud_establishments.get_establishment(db, establishment_id)
    if not establishment:
        raise HTTPException(status_code=404, detail="Establishment not found")
    return establishment


@router.post("/", response_model=EstablishmentResponse)
def create_establishment(
    establishment: EstablishmentCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_owner_or_admin()),
):
    """Create establishment (Owner or Admin only)"""
    user_role = get_user_role_name(current_user)
    
    # Owners can only create establishments for themselves
    if user_role == RoleType.DUENO.value:
        if establishment.usuario_id != current_user.usuario_id:
            raise HTTPException(
                status_code=403,
                detail="Owners can only create establishments for themselves",
            )
    
    try:
        return crud_establishments.create_establishment(db, establishment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{establishment_id}", response_model=EstablishmentResponse)
def update_establishment(
    establishment_id: int,
    establishment: EstablishmentUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_owner_or_admin()),
):
    """Update establishment (Owner of establishment or Admin)"""
    db_establishment = crud_establishments.get_establishment(db, establishment_id)
    if not db_establishment:
        raise HTTPException(status_code=404, detail="Establishment not found")
    
    validate_establishment_access(current_user, db_establishment)
    
    db_establishment = crud_establishments.update_establishment(db, establishment_id, establishment)
    return db_establishment


@router.patch("/{establishment_id}", response_model=EstablishmentResponse)
def patch_establishment(
    establishment_id: int,
    establishment: EstablishmentUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_owner_or_admin()),
):
    """Partially update establishment (Owner of establishment or Admin)"""
    db_establishment = crud_establishments.get_establishment(db, establishment_id)
    if not db_establishment:
        raise HTTPException(status_code=404, detail="Establishment not found")
    
    validate_establishment_access(current_user, db_establishment)
    
    db_establishment = crud_establishments.update_establishment(db, establishment_id, establishment)
    return db_establishment


@router.delete("/{establishment_id}")
def delete_establishment(
    establishment_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_owner_or_admin()),
):
    """Delete establishment (Owner of establishment or Admin)"""
    db_establishment = crud_establishments.get_establishment(db, establishment_id)
    if not db_establishment:
        raise HTTPException(status_code=404, detail="Establishment not found")
    
    validate_establishment_access(current_user, db_establishment)
    
    success = crud_establishments.delete_establishment(db, establishment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Establishment not found")
    return {"message": "Establishment deleted successfully"}