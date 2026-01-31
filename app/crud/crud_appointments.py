from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Appointment, Service, User
from app.schemas.appointments import AppointmentCreate, AppointmentUpdate


def get_appointment(db: Session, appointment_id: int) -> Optional[Appointment]:
    return db.query(Appointment).filter(Appointment.cita_id == appointment_id).first()


def get_appointments(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    cliente_id: Optional[int] = None,
    servicio_id: Optional[int] = None,
) -> List[Appointment]:
    query = db.query(Appointment)
    if cliente_id is not None:
        query = query.filter(Appointment.cliente_id == cliente_id)
    if servicio_id is not None:
        query = query.filter(Appointment.servicio_id == servicio_id)
    return query.offset(skip).limit(limit).all()


def create_appointment(db: Session, appointment: AppointmentCreate) -> Appointment:
    # Verify cliente_id exists
    client = db.query(User).filter(User.usuario_id == appointment.cliente_id).first()
    if not client:
        raise ValueError(f"User with id {appointment.cliente_id} does not exist")
    
    # Verify servicio_id exists
    service = db.query(Service).filter(Service.servicio_id == appointment.servicio_id).first()
    if not service:
        raise ValueError(f"Service with id {appointment.servicio_id} does not exist")
    
    appointment_data = appointment.model_dump()
    db_appointment = Appointment(**appointment_data)  # type: ignore[arg-type]
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment


def update_appointment(
    db: Session,
    appointment_id: int,
    appointment: AppointmentUpdate,
) -> Optional[Appointment]:
    db_appointment = get_appointment(db, appointment_id)
    if not db_appointment:
        return None

    update_data = appointment.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_appointment, field, value)

    db.commit()
    db.refresh(db_appointment)
    return db_appointment


def delete_appointment(db: Session, appointment_id: int) -> bool:
    db_appointment = get_appointment(db, appointment_id)
    if not db_appointment:
        return False

    db.delete(db_appointment)
    db.commit()
    return True
