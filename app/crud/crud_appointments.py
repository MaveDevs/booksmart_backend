from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.crud import crud_notifications
from app.models import Appointment, Service, User
from app.models.establishments import Establishment
from app.models.notifications import NotificationType
from app.schemas.appointments import AppointmentCreate, AppointmentUpdate
from app.schemas.notifications import NotificationCreate


def get_appointment(db: Session, appointment_id: int) -> Optional[Appointment]:
    return (
        db.query(Appointment)
        .options(joinedload(Appointment.client), joinedload(Appointment.worker), joinedload(Appointment.service))
        .filter(Appointment.cita_id == appointment_id)
        .first()
    )


def get_appointments(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    cliente_id: Optional[int] = None,
    servicio_id: Optional[int] = None,
    trabajador_id: Optional[int] = None,
    establishment_id: Optional[int] = None,
) -> List[Appointment]:
    query = db.query(Appointment)
    
    # If establishment filter is needed, join with Service
    if establishment_id is not None:
        query = query.join(Service).filter(Service.establecimiento_id == establishment_id)
        
    query = query.options(
        joinedload(Appointment.client), 
        joinedload(Appointment.worker), 
        joinedload(Appointment.service)
    )
    
    if cliente_id is not None:
        query = query.filter(Appointment.cliente_id == cliente_id)
    if servicio_id is not None:
        query = query.filter(Appointment.servicio_id == servicio_id)
    if trabajador_id is not None:
        query = query.filter(Appointment.trabajador_id == trabajador_id)
        
    return query.offset(skip).limit(limit).all()


def _build_status_notification_message(
    db: Session,
    appointment: Appointment,
    service: Service,
    notification_event: str,
    reason: Optional[str] = None,
) -> str:
    business_name = None
    service_name = getattr(service, "nombre", None)

    establishment = getattr(service, "establishment", None)
    if establishment:
        business_name = getattr(establishment, "nombre", None)

    if not business_name and getattr(service, "establecimiento_id", None) is not None:
        establishment = (
            db.query(Establishment)
            .filter(Establishment.establecimiento_id == service.establecimiento_id)
            .first()
        )
        if establishment:
            business_name = getattr(establishment, "nombre", None)

    business_name = business_name or "tu negocio"
    service_name = service_name or "tu servicio"

    appointment_date = appointment.fecha.strftime("%d/%m/%Y")
    appointment_time = appointment.hora_inicio.strftime("%H:%M")
    base_message = (
        f"Tu cita en {business_name} para el servicio {service_name} el {appointment_date} a las {appointment_time}"
    )

    if notification_event == "confirmed":
        return f"{base_message} fue confirmada."
    if notification_event == "rejected":
        return f"{base_message} fue rechazada."
    if notification_event == "cancelled":
        if reason:
            return f"{base_message} fue cancelada. Motivo: {reason}"
        return f"{base_message} fue cancelada."
    if notification_event == "completed":
        return f"{base_message} fue marcada como completada."

    return base_message


def _create_status_notification(
    db: Session,
    appointment: Appointment,
    service: Service,
    notification_event: str,
    reason: Optional[str] = None,
) -> None:
    message = _build_status_notification_message(
        db,
        appointment,
        service,
        notification_event,
        reason=reason,
    )

    crud_notifications.create_notification(
        db,
        NotificationCreate(
            usuario_id=appointment.cliente_id,
            mensaje=message,
            tipo=NotificationType.ALERTA,
            leida=False,
        ),
    )


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

    from app.services.notification_orchestrator import orchestrator

    orchestrator.on_appointment_created_sync(
        db, db_appointment.cita_id, service.establecimiento_id
    )

    return db_appointment


def update_appointment(
    db: Session,
    appointment_id: int,
    appointment: AppointmentUpdate,
    notification_event: Optional[str] = None,
) -> Optional[Appointment]:
    from app.services.notification_orchestrator import orchestrator

    db_appointment = get_appointment(db, appointment_id)
    if not db_appointment:
        return None

    previous_status = db_appointment.estado

    update_data = appointment.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_appointment, field, value)

    db.commit()
    db.refresh(db_appointment)

    service = db.query(Service).filter(Service.servicio_id == db_appointment.servicio_id).first()
    if not service:
        return db_appointment

    new_status = db_appointment.estado
    if new_status == previous_status:
        return db_appointment

    if new_status.value == "CONFIRMADA":
        try:
            _create_status_notification(
                db,
                db_appointment,
                service,
                notification_event or "confirmed",
            )
        except Exception:
            import logging

            logging.exception("Failed to create confirmation notification for appointment %s", db_appointment.cita_id)
        orchestrator.on_appointment_confirmed_sync(
            db,
            db_appointment.cita_id,
            service.establecimiento_id,
            create_endpoint_notification=False,
        )
    elif new_status.value == "CANCELADA":
        try:
            _create_status_notification(
                db,
                db_appointment,
                service,
                notification_event or "cancelled",
            )
        except Exception:
            import logging

            logging.exception("Failed to create cancellation notification for appointment %s", db_appointment.cita_id)
        orchestrator.on_appointment_cancelled_sync(
            db,
            db_appointment.cita_id,
            service.establecimiento_id,
            create_endpoint_notification=False,
        )
    elif new_status.value == "COMPLETADA":
        try:
            _create_status_notification(
                db,
                db_appointment,
                service,
                notification_event or "completed",
            )
        except Exception:
            import logging

            logging.exception("Failed to create completion notification for appointment %s", db_appointment.cita_id)
        orchestrator.on_appointment_completed_sync(
            db,
            db_appointment.cita_id,
            service.establecimiento_id,
            create_endpoint_notification=False,
        )

    return db_appointment


def delete_appointment(db: Session, appointment_id: int) -> bool:
    db_appointment = get_appointment(db, appointment_id)
    if not db_appointment:
        return False

    db.delete(db_appointment)
    db.commit()
    return True
