from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.core.permissions import (
    require_admin,
    validate_own_resource,
    get_user_role_name,
    RoleType,
)
from app.crud import crud_users
from app.models import User
from app.schemas.users import UserCreate, UserUpdate, UserResponse

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_admin()),
):
    """Get all users (Admin only)"""
    return crud_users.get_users(db, skip=skip, limit=limit)


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(deps.get_current_user),
):
    """Get current user's own information"""
    return current_user


@router.get("/by-email/{email}", response_model=UserResponse)
def get_user_by_email(
    email: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_admin()),
):
    """Get user by email (Admin only)"""
    user = crud_users.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Get user by ID (own profile or admin)"""
    # Users can only view their own profile unless admin
    user_role = get_user_role_name(current_user)
    if user_role != RoleType.ADMIN.value and current_user.usuario_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only view your own profile",
        )
    
    user = crud_users.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(deps.get_db)):
    """Create new user (public registration)"""
    db_user = crud_users.get_user_by_email(db, email=user.correo)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    try:
        return crud_users.create_user(db, user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Update user (own profile or admin)"""
    user_role = get_user_role_name(current_user)
    
    # Only admin can change roles
    if user.rol_id is not None and user_role != RoleType.ADMIN.value:
        raise HTTPException(
            status_code=403,
            detail="Only admin can change user roles",
        )
    
    # Users can only update their own profile unless admin
    if user_role != RoleType.ADMIN.value and current_user.usuario_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only update your own profile",
        )
    
    try:
        db_user = crud_users.update_user(db, user_id, user)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        return db_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{user_id}", response_model=UserResponse)
def patch_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Partially update user (own profile or admin)"""
    user_role = get_user_role_name(current_user)
    
    # Only admin can change roles
    if user.rol_id is not None and user_role != RoleType.ADMIN.value:
        raise HTTPException(
            status_code=403,
            detail="Only admin can change user roles",
        )
    
    # Users can only update their own profile unless admin
    if user_role != RoleType.ADMIN.value and current_user.usuario_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only update your own profile",
        )
    
    try:
        db_user = crud_users.update_user(db, user_id, user)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        return db_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_admin()),
):
    """Delete user (Admin only)"""
    success = crud_users.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}