"""
Role-based permission system for Booksmart.

Roles:
- CLIENTE (Client): Book appointments, leave reviews, read establishments
- DUEÑO (Owner): Manage their own business, services, appointments
- ADMIN: Full system access

Usage in endpoints:
    from app.core.permissions import require_role, require_owner_or_admin, RoleType
    
    @router.get("/")
    def get_items(current_user: User = Depends(require_role(RoleType.ADMIN))):
        ...
"""

from enum import Enum
from typing import List, Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import User, Establishment, Appointment, Service


class RoleType(str, Enum):
    """Role types matching database role names."""
    CLIENTE = "cliente"
    DUENO = "dueño"
    ADMIN = "admin"
    TRABAJADOR = "trabajador"


def get_user_role_name(user: User) -> Optional[str]:
    """Get the role name of a user (lowercase for comparison)."""
    if user.role:
        return user.role.nombre.lower()

    if user.rol_id == 1:
        return RoleType.CLIENTE.value
    if user.rol_id == 2:
        return RoleType.DUENO.value
    if user.rol_id == 3:
        return RoleType.ADMIN.value
    if user.rol_id == 4:
        return RoleType.TRABAJADOR.value

    return None


def require_role(*allowed_roles: RoleType):
    """
    Dependency that requires the user to have one of the specified roles.
    
    Usage:
        @router.get("/admin-only")
        def admin_endpoint(user: User = Depends(require_role(RoleType.ADMIN))):
            ...
        
        @router.get("/owner-or-admin")
        def owner_endpoint(user: User = Depends(require_role(RoleType.DUENO, RoleType.ADMIN))):
            ...
    """
    def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        user_role = get_user_role_name(current_user)
        
        if user_role is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User has no assigned role",
            )
        
        allowed_role_values = [role.value for role in allowed_roles]
        if user_role not in allowed_role_values:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {', '.join(allowed_role_values)}",
            )
        
        return current_user
    
    return role_checker


def require_admin():
    """Shortcut for admin-only endpoints."""
    return require_role(RoleType.ADMIN)


def require_owner_or_admin():
    """Shortcut for owner or admin endpoints."""
    return require_role(RoleType.DUENO, RoleType.ADMIN)


def require_any_authenticated():
    """Any authenticated user (all roles)."""
    return require_role(RoleType.CLIENTE, RoleType.DUENO, RoleType.ADMIN)


# ============================================================================
# Resource-specific permission checks
# ============================================================================

def check_owns_establishment(
    db: Session,
    user: User,
    establecimiento_id: int,
) -> bool:
    """Check if user owns the establishment."""
    establishment = (
        db.query(Establishment)
        .filter(Establishment.establecimiento_id == establecimiento_id)
        .first()
    )
    if not establishment:
        return False
    return establishment.usuario_id == user.usuario_id


def check_is_appointment_client(
    db: Session,
    user: User,
    cita_id: int,
) -> bool:
    """Check if user is the client of the appointment."""
    appointment = (
        db.query(Appointment)
        .filter(Appointment.cita_id == cita_id)
        .first()
    )
    if not appointment:
        return False
    return appointment.cliente_id == user.usuario_id


def check_owns_appointment_establishment(
    db: Session,
    user: User,
    cita_id: int,
) -> bool:
    """Check if user owns the establishment where the appointment is."""
    appointment = (
        db.query(Appointment)
        .filter(Appointment.cita_id == cita_id)
        .first()
    )
    if not appointment:
        return False
    
    # Get the service to find the establishment
    service = (
        db.query(Service)
        .filter(Service.servicio_id == appointment.servicio_id)
        .first()
    )
    if not service:
        return False
    
    return check_owns_establishment(db, user, service.establecimiento_id)


def check_owns_service_establishment(
    db: Session,
    user: User,
    servicio_id: int,
) -> bool:
    """Check if user owns the establishment of the service."""
    service = (
        db.query(Service)
        .filter(Service.servicio_id == servicio_id)
        .first()
    )
    if not service:
        return False
    return check_owns_establishment(db, user, service.establecimiento_id)


# ============================================================================
# Permission validation helpers for endpoints
# ============================================================================

def validate_establishment_access(
    user: User,
    establishment,
    require_ownership: bool = True,
) -> None:
    """
    Validate user has access to establishment.
    - Admin: always has access
    - Owner: only if they own it (when require_ownership=True)
    - Client: read-only access (when require_ownership=False)
    
    Args:
        user: The current user
        establishment: The establishment object
        require_ownership: If True, owner must own it. If False, any role can access.
    """
    user_role = get_user_role_name(user)
    
    # Admin has full access
    if user_role == RoleType.ADMIN.value:
        return
    
    # Owner must own the establishment for write operations
    if require_ownership:
        if user_role == RoleType.DUENO.value:
            if establishment.usuario_id != user.usuario_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't own this establishment",
                )
            return
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only owners can modify establishments",
            )
    
    # For read-only, any authenticated user can access
    return


def validate_appointment_access(
    db: Session,
    user: User,
    cita_id: int,
    allow_client: bool = True,
    allow_owner: bool = True,
) -> None:
    """
    Validate user has access to appointment.
    - Admin: always has access
    - Owner: if they own the establishment
    - Client: if they are the client of the appointment
    """
    user_role = get_user_role_name(user)
    
    # Admin has full access
    if user_role == RoleType.ADMIN.value:
        return
    
    # Check owner access
    if allow_owner and user_role == RoleType.DUENO.value:
        if check_owns_appointment_establishment(db, user, cita_id):
            return
    
    # Check client access
    if allow_client and user_role == RoleType.CLIENTE.value:
        if check_is_appointment_client(db, user, cita_id):
            return
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You don't have access to this appointment",
    )


def validate_own_resource(
    user: User,
    resource_user_id: int,
    resource_name: str = "resource",
) -> None:
    """
    Validate user owns the resource or is admin.
    Used for reviews, notifications, etc.
    """
    user_role = get_user_role_name(user)
    
    # Admin has full access
    if user_role == RoleType.ADMIN.value:
        return
    
    # User must own the resource
    if user.usuario_id != resource_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You don't own this {resource_name}",
        )
