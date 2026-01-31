from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.core.permissions import require_admin
from app.crud import crud_roles
from app.models import User
from app.schemas.rol import RoleCreate, RoleResponse, RoleUpdate

router = APIRouter()


@router.get("/", response_model=List[RoleResponse])
def get_roles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_admin()),
):
    """Get all roles (Admin only)"""
    return crud_roles.get_roles(db, skip=skip, limit=limit)


@router.get("/{role_id}", response_model=RoleResponse)
def get_role(
    role_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_admin()),
):
    """Get role by ID (Admin only)"""
    role = crud_roles.get_role(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.post("/", response_model=RoleResponse)
def create_role(
    role: RoleCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_admin()),
):
    """Create new role (Admin only)"""
    return crud_roles.create_role(db, role)


@router.put("/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: int,
    role: RoleUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_admin()),
):
    """Update role (Admin only)"""
    db_role = crud_roles.update_role(db, role_id, role)
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role


@router.patch("/{role_id}", response_model=RoleResponse)
def patch_role(
    role_id: int,
    role: RoleUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_admin()),
):
    """Partially update role (Admin only)"""
    db_role = crud_roles.update_role(db, role_id, role)
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role


@router.delete("/{role_id}")
def delete_role(
    role_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_admin()),
):
    """Delete role (Admin only)"""
    success = crud_roles.delete_role(db, role_id)
    if not success:
        raise HTTPException(status_code=404, detail="Role not found")
    return {"message": "Role deleted successfully"}
