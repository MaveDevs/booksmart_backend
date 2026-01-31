from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import crud_profiles, crud_establishments
from app.models import User
from app.schemas.profiles import ProfileCreate, ProfileResponse, ProfileUpdate
from app.core.permissions import (
    require_owner_or_admin,
    validate_establishment_access,
)

router = APIRouter()


@router.get("/", response_model=List[ProfileResponse])
def get_profiles(
    establecimiento_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Any authenticated user can list profiles (read-only)."""
    return crud_profiles.get_profiles(db, skip=skip, limit=limit, establecimiento_id=establecimiento_id)


@router.get("/{profile_id}", response_model=ProfileResponse)
def get_profile(
    profile_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Any authenticated user can view a profile (read-only)."""
    profile = crud_profiles.get_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.post("/", response_model=ProfileResponse)
def create_profile(
    profile: ProfileCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_owner_or_admin()),
):
    """Only owners and admins can create profiles. Owners can only create profiles for their own establishments."""
    # Verify establishment exists and user has access
    establishment = crud_establishments.get_establishment(db, profile.establecimiento_id)
    if not establishment:
        raise HTTPException(status_code=404, detail="Establishment not found")
    
    # Owners can only create profiles for their own establishments
    validate_establishment_access(current_user, establishment)
    
    try:
        return crud_profiles.create_profile(db, profile)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{profile_id}", response_model=ProfileResponse)
def update_profile(
    profile_id: int,
    profile: ProfileUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_owner_or_admin()),
):
    """Only owners and admins can update profiles. Owners can only update profiles for their own establishments."""
    db_profile = crud_profiles.get_profile(db, profile_id)
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Verify user has access to the establishment this profile belongs to
    establishment = crud_establishments.get_establishment(db, db_profile.establecimiento_id)
    if establishment:
        validate_establishment_access(current_user, establishment)
    
    db_profile = crud_profiles.update_profile(db, profile_id, profile)
    return db_profile


@router.patch("/{profile_id}", response_model=ProfileResponse)
def patch_profile(
    profile_id: int,
    profile: ProfileUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_owner_or_admin()),
):
    """Only owners and admins can patch profiles. Owners can only patch profiles for their own establishments."""
    db_profile = crud_profiles.get_profile(db, profile_id)
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Verify user has access to the establishment this profile belongs to
    establishment = crud_establishments.get_establishment(db, db_profile.establecimiento_id)
    if establishment:
        validate_establishment_access(current_user, establishment)
    
    db_profile = crud_profiles.update_profile(db, profile_id, profile)
    return db_profile


@router.delete("/{profile_id}")
def delete_profile(
    profile_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_owner_or_admin()),
):
    """Only owners and admins can delete profiles. Owners can only delete profiles for their own establishments."""
    db_profile = crud_profiles.get_profile(db, profile_id)
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Verify user has access to the establishment this profile belongs to
    establishment = crud_establishments.get_establishment(db, db_profile.establecimiento_id)
    if establishment:
        validate_establishment_access(current_user, establishment)
    
    success = crud_profiles.delete_profile(db, profile_id)
    if not success:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"message": "Profile deleted successfully"}
