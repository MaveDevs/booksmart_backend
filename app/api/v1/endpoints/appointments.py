from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import crud_appointments, crud_services, crud_establishments
from app.models import User
from app.schemas.appointments import AppointmentCreate, AppointmentResponse, AppointmentUpdate
from app.core.permissions import (
    RoleType,
    get_user_role_name,
    require_admin,
    require_owner_or_admin,
)

router = APIRouter()


def _user_can_access_appointment(db: Session, user: User, appointment) -> bool:
    """Check if user can access this appointment (is client or owns establishment)."""
    user_role = get_user_role_name(user)
    
    # Admin can access all
    if user_role == RoleType.ADMIN.value:
        return True
    
    # Client can access their own appointments
    if appointment.cliente_id == user.usuario_id:
        return True
    
    # Owner can access appointments for their establishment's services
    if user_role == RoleType.DUENO.value:
        service = crud_services.get_service(db, appointment.servicio_id)
        if service:
            establishment = crud_establishments.get_establishment(db, service.establecimiento_id)
            if establishment and establishment.usuario_id == user.usuario_id:
                return True
    
    return False


@router.get("/", response_model=List[AppointmentResponse])
def get_appointments(
    cliente_id: Optional[int] = Query(None),
    servicio_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    List appointments filtered by access:
    - Clients: can only see their own appointments
    - Owners: can see appointments for their establishments
    - Admins: can see all appointments
    """
    user_role = get_user_role_name(current_user)
    
    # Admin can see all
    if user_role == RoleType.ADMIN.value:
        return crud_appointments.get_appointments(
            db, skip=skip, limit=limit, cliente_id=cliente_id, servicio_id=servicio_id
        )
    
    # Clients can only see their own appointments
    if user_role == RoleType.CLIENTE.value:
        return crud_appointments.get_appointments(
            db, skip=skip, limit=limit, cliente_id=current_user.usuario_id, servicio_id=servicio_id
        )
    
    # Owners: if servicio_id given, verify they own it; otherwise get appointments for their establishments
    if user_role == RoleType.DUENO.value:
        if servicio_id:
            service = crud_services.get_service(db, servicio_id)
            if service:
                establishment = crud_establishments.get_establishment(db, service.establecimiento_id)
                if not establishment or establishment.usuario_id != current_user.usuario_id:
                    raise HTTPException(status_code=403, detail="You don't own this service's establishment")
            return crud_appointments.get_appointments(
                db, skip=skip, limit=limit, servicio_id=servicio_id
            )
        # Get all appointments for owner's establishments
        establishments = crud_establishments.get_establishments_by_user(db, current_user.usuario_id)
        all_appointments = []
        for est in establishments:
            services = crud_services.get_services_by_establishment(db, est.establecimiento_id)
            for svc in services:
                appts = crud_appointments.get_appointments(db, servicio_id=svc.servicio_id)
                all_appointments.extend(appts)
        return all_appointments[skip:skip + limit]
    
    return []


@router.get("/me", response_model=List[AppointmentResponse])
def get_my_appointments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Get current user's appointments as a client."""
    return crud_appointments.get_appointments(
        db, skip=skip, limit=limit, cliente_id=current_user.usuario_id
    )


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Get a specific appointment. Users can only access appointments they're involved in."""
    appointment = crud_appointments.get_appointment(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    if not _user_can_access_appointment(db, current_user, appointment):
        raise HTTPException(status_code=403, detail="You don't have access to this appointment")
    
    return appointment


@router.post("/", response_model=AppointmentResponse)
def create_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Create an appointment.
    - Clients can create appointments for themselves (cliente_id must match their user id)
    - Admins can create appointments for anyone
    """
    user_role = get_user_role_name(current_user)
    
    # Clients can only create appointments for themselves
    if user_role == RoleType.CLIENTE.value:
        if appointment.cliente_id != current_user.usuario_id:
            raise HTTPException(
                status_code=403,
                detail="You can only create appointments for yourself"
            )
    
    try:
        return crud_appointments.create_appointment(db, appointment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    appointment: AppointmentUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Update an appointment.
    - Clients can only cancel their own appointments (change estado)
    - Owners can update status (accept/reject/complete) for their establishment's appointments
    - Admins can update any appointment
    """
    db_appointment = crud_appointments.get_appointment(db, appointment_id)
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    if not _user_can_access_appointment(db, current_user, db_appointment):
        raise HTTPException(status_code=403, detail="You don't have access to this appointment")
    
    db_appointment = crud_appointments.update_appointment(db, appointment_id, appointment)
    return db_appointment


@router.patch("/{appointment_id}", response_model=AppointmentResponse)
def patch_appointment(
    appointment_id: int,
    appointment: AppointmentUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Partial update for an appointment. Same access rules as PUT."""
    db_appointment = crud_appointments.get_appointment(db, appointment_id)
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    if not _user_can_access_appointment(db, current_user, db_appointment):
        raise HTTPException(status_code=403, detail="You don't have access to this appointment")
    
    db_appointment = crud_appointments.update_appointment(db, appointment_id, appointment)
    return db_appointment


@router.delete("/{appointment_id}")
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_admin()),
):
    """Only admins can delete appointments. Use PATCH to cancel."""
    success = crud_appointments.delete_appointment(db, appointment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return {"message": "Appointment deleted successfully"}
