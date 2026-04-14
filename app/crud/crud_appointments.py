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
    
    from app.models.workers import Worker
    from datetime import datetime, timedelta

    # Auto-assignment logic if trabajador_id is not provided
    assigned_worker_id = appointment.trabajador_id

    if not assigned_worker_id:
        # Find all workers that offer this service
        qualified_workers = db.query(Worker).join(Worker.services).filter(
            Service.servicio_id == appointment.servicio_id,
            Worker.establecimiento_id == service.establecimiento_id,
            Worker.activo == True
        ).all()

        if not qualified_workers:
            raise ValueError("No hay profesionales registrados que realicen este servicio.")

        # For each qualified worker, check if they are busy at this time
        # We'll pick the first one who is free
        # A more advanced version could pick the one with the least load
        best_worker_id = None
        
        # Calculate end time for the potential appointment
        end_time = (datetime.combine(appointment.fecha, appointment.hora_inicio) + timedelta(minutes=service.duracion)).time()

        for worker in qualified_workers:
            # Check for overlapping appointments for THIS worker
            conflict = db.query(Appointment).filter(
                Appointment.trabajador_id == worker.trabajador_id,
                Appointment.fecha == appointment.fecha,
                Appointment.estado.in_(["CONFIRMADA", "PENDIENTE"]),
                Appointment.hora_inicio < end_time,
                Appointment.hora_fin > appointment.hora_inicio
            ).first()

            if not conflict:
                best_worker_id = worker.trabajador_id
                break
        
        if not best_worker_id:
            raise ValueError("Lo sentimos, no hay profesionales disponibles en el horario seleccionado.")
        
        assigned_worker_id = best_worker_id

    else:
        # Validate that the manually selected worker actually performs this service
        worker = db.query(Worker).filter(Worker.trabajador_id == assigned_worker_id).first()
        if not worker or worker.establecimiento_id != service.establecimiento_id:
            raise ValueError("El profesional seleccionado no pertenece a este negocio.")
        
        # Check if the selected worker offers this service
        service_ids = [s.servicio_id for s in worker.services]
        if service.servicio_id not in service_ids:
            raise ValueError(f"El profesional {worker.nombre} no ofrece el servicio seleccionado.")

        # Check for conflicts for the specific worker
        end_time = (datetime.combine(appointment.fecha, appointment.hora_inicio) + timedelta(minutes=service.duracion)).time()
        conflict = db.query(Appointment).filter(
            Appointment.trabajador_id == assigned_worker_id,
            Appointment.fecha == appointment.fecha,
            Appointment.estado.in_(["CONFIRMADA", "PENDIENTE"]),
            Appointment.hora_inicio < end_time,
            Appointment.hora_fin > appointment.hora_inicio
        ).first()

        if conflict:
            raise ValueError("El profesional seleccionado ya tiene una cita en ese horario.")

    # Calculate final duration based on service
    final_hora_fin = (datetime.combine(appointment.fecha, appointment.hora_inicio) + timedelta(minutes=service.duracion)).time()

    appointment_data = appointment.model_dump()
    appointment_data["trabajador_id"] = assigned_worker_id
    appointment_data["hora_fin"] = final_hora_fin
    
    db_appointment = Appointment(**appointment_data)
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
