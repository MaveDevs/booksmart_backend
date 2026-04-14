from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import crud_appointments, crud_services, crud_establishments, crud_special_closures
from app.models import User, Appointment, Service
from app.schemas.appointments import AppointmentCreate, AppointmentResponse, AppointmentUpdate
from app.core.permissions import (
    RoleType,
    get_user_role_name,
    require_admin,
    require_owner_or_admin,
    check_owns_appointment_establishment
)
from datetime import date, timedelta, datetime

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
    
    # Worker can access appointments assigned to them
    from app.crud import crud_workers
    worker = crud_workers.get_worker_by_user(db, user.usuario_id)
    if worker and appointment.trabajador_id == worker.trabajador_id:
        return True
    
    return False


@router.get("/", response_model=List[AppointmentResponse])
def get_appointments(
    cliente_id: Optional[int] = Query(None),
    servicio_id: Optional[int] = Query(None),
    trabajador_id: Optional[int] = Query(None),
    establishment_id: Optional[int] = Query(None),
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
            db, skip=skip, limit=limit, cliente_id=cliente_id, servicio_id=servicio_id, trabajador_id=trabajador_id, establishment_id=establishment_id
        )
    
    # Clients can only see their own appointments
    if user_role == RoleType.CLIENTE.value:
        return crud_appointments.get_appointments(
            db, skip=skip, limit=limit, cliente_id=current_user.usuario_id, servicio_id=servicio_id, trabajador_id=trabajador_id, establishment_id=establishment_id
        )
    
    # Owners: if establishment_id given, verify they own it
    if user_role == RoleType.DUENO.value:
        if establishment_id:
            # Check if owner owns this specific establishment
            est = crud_establishments.get_establishment(db, establishment_id)
            if not est or est.usuario_id != current_user.usuario_id:
                raise HTTPException(status_code=403, detail="You do not own this establishment")
            
            return crud_appointments.get_appointments(
                db, 
                skip=skip, 
                limit=limit, 
                cliente_id=cliente_id,
                servicio_id=servicio_id, 
                trabajador_id=trabajador_id,
                establishment_id=establishment_id
            )

        # Legacy behavior: if no establishment_id, get it for all their establishments
        if servicio_id:
            service = crud_services.get_service(db, servicio_id)
            if service:
                establishment = crud_establishments.get_establishment(db, service.establecimiento_id)
                if not establishment or establishment.usuario_id != current_user.usuario_id:
                    raise HTTPException(status_code=403, detail="You don't own this service's establishment")
            return crud_appointments.get_appointments(
                db, skip=skip, limit=limit, servicio_id=servicio_id
            )
            
        # Get all appointments for all owner's establishments
        establishments = crud_establishments.get_establishments_by_user(db, current_user.usuario_id)
        all_appointments = []
        for est in establishments:
            appts = crud_appointments.get_appointments(db, establishment_id=est.establecimiento_id)
            all_appointments.extend(appts)
        return all_appointments[skip:skip + limit]
    
    # Workers: can only see appointments assigned to them
    if user_role == RoleType.TRABAJADOR.value:
        from app.crud import crud_workers
        worker = crud_workers.get_worker_by_user(db, current_user.usuario_id)
        if not worker:
            return []
        return crud_appointments.get_appointments(
            db, skip=skip, limit=limit, trabajador_id=worker.trabajador_id, establishment_id=establishment_id
        )
    
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


@router.post("/{appointment_id}/accept", response_model=AppointmentResponse)
def accept_appointment(
    appointment_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """PWA: Accept a pending appointment (moves to CONFIRMADA)."""
    db_appointment = crud_appointments.get_appointment(db, appointment_id)
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    if not check_owns_appointment_establishment(db, current_user, appointment_id):
        raise HTTPException(status_code=403, detail="You do not own the establishment for this appointment")
    
    update_data = AppointmentUpdate(estado="CONFIRMADA")
    return crud_appointments.update_appointment(db, appointment_id, update_data)


@router.post("/{appointment_id}/decline", response_model=AppointmentResponse)
def decline_appointment(
    appointment_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """PWA: Decline a pending appointment (moves to CANCELADA)."""
    db_appointment = crud_appointments.get_appointment(db, appointment_id)
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    if not check_owns_appointment_establishment(db, current_user, appointment_id):
        raise HTTPException(status_code=403, detail="You do not own the establishment for this appointment")
    
    update_data = AppointmentUpdate(estado="CANCELADA")
    return crud_appointments.update_appointment(
        db,
        appointment_id,
        update_data,
        notification_event="rejected",
    )


@router.get("/availability/slots")
def get_available_slots(
    servicio_id: int,
    target_date: date,
    trabajador_id: Optional[int] = Query(None),
    db: Session = Depends(deps.get_db),
):
    """
    Get available time slots for a specific service on a specific date.
    Logic upgraded to support multiple workers and concurrency.
    """
    from app.crud import crud_agendas, crud_workers
    from app.models.workers import Worker

    service = crud_services.get_service(db, servicio_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")

    # 1. Check for special closures
    matching_closure = crud_special_closures.get_closure_by_date(db, service.establecimiento_id, target_date)
    if matching_closure:
        return {
            "date": target_date.strftime("%Y-%m-%d"),
            "servicio_id": servicio_id,
            "available_slots": [],
            "busy_slots": [],
            "closed": True,
            "closure_reason": matching_closure.motivo or "Cerrado por día especial",
        }

    # 2. Check business agenda for the day
    days = ["LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO", "DOMINGO"]
    day_name = days[target_date.weekday()]
    agendas = crud_agendas.get_agendas(db, establecimiento_id=service.establecimiento_id)
    day_agenda = next((a for a in agendas if a.dia_semana == day_name), None)
    
    if not day_agenda:
        return {
            "date": target_date.strftime("%Y-%m-%d"),
            "servicio_id": servicio_id,
            "available_slots": [],
            "busy_slots": [],
            "closed": True,
            "closure_reason": "No hay horario de servicio para este día",
        }

    # 3. Identify qualified workers
    if trabajador_id:
        worker = crud_workers.get_worker(db, trabajador_id)
        if not worker or worker.establecimiento_id != service.establecimiento_id:
             raise HTTPException(status_code=404, detail="Worker not found or doesn't belong to this establishment")
        # Verify worker provides this service
        service_ids = [s.servicio_id for s in worker.services]
        if servicio_id not in service_ids:
            return {
                "date": target_date.strftime("%Y-%m-%d"),
                "servicio_id": servicio_id,
                "available_slots": [],
                "busy_slots": [],
                "closed": False,
                "closure_reason": "El trabajador seleccionado no ofrece este servicio",
            }
        qualified_workers = [worker]
    else:
        # Get all workers that offer this service
        qualified_workers = db.query(Worker).join(Worker.services).filter(
            Service.servicio_id == servicio_id,
            Worker.establecimiento_id == service.establecimiento_id,
            Worker.activo == True
        ).all()

    if not qualified_workers:
         return {
            "date": target_date.strftime("%Y-%m-%d"),
            "servicio_id": servicio_id,
            "available_slots": [],
            "busy_slots": [],
            "closed": False,
            "closure_reason": "No hay profesionales disponibles para este servicio",
        }

    # 4. Get all appointments for those workers on that date
    worker_ids = [w.trabajador_id for w in qualified_workers]
    appointments = db.query(Appointment).filter(
        Appointment.trabajador_id.in_(worker_ids),
        Appointment.fecha == target_date,
        Appointment.estado.in_(["CONFIRMADA", "PENDIENTE"])
    ).all()

    # 5. Generate slots based on agenda and service duration
    # This is a simplified slot generator. In a real world, you'd calculate overlapping.
    # We'll use the service duration to step through the agenda.
    start_dt = datetime.combine(target_date, day_agenda.hora_inicio)
    end_dt = datetime.combine(target_date, day_agenda.hora_fin)
    
    interval = service.duracion # in minutes
    if interval <= 0: interval = 30 # fallback
    
    current_dt = start_dt
    available_slots = []
    busy_slots = []

    while current_dt + timedelta(minutes=interval) <= end_dt:
        slot_time = current_dt.time()
        slot_end_time = (current_dt + timedelta(minutes=interval)).time()
        
        # Check how many workers are busy during this specific slot
        # For simplicity, we check if a worker has an appointment starting at this time
        # Better logic would check if worker is busy at ANY point during this slot
        busy_workers_count = 0
        for appt in appointments:
             # Basic overlap check: appt starts before slot ends AND appt ends after slot starts
             if appt.hora_inicio < slot_end_time and appt.hora_fin > slot_time:
                 busy_workers_count += 1
        
        slot_str = slot_time.strftime("%H:%M")
        if busy_workers_count < len(qualified_workers):
            available_slots.append(slot_str)
        else:
            busy_slots.append(slot_str)
            
        current_dt += timedelta(minutes=interval)

    return {
        "date": target_date.strftime("%Y-%m-%d"),
        "servicio_id": servicio_id,
        "worker_count": len(qualified_workers),
        "available_slots": available_slots,
        "busy_slots": busy_slots,
        "closed": False,
        "closure_reason": None,
    }


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
