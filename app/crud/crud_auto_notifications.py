"""
CRUD operations for Automatic Notifications
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import AutoNotification
from app.models.auto_notifications import AutoNotificationType, AutoNotificationStatus, NotificationChannel
from app.schemas.auto_notifications import AutoNotificationCreate, AutoNotificationUpdate


def get_auto_notification(db: Session, notif_auto_id: int) -> Optional[AutoNotification]:
    """Get a specific auto notification"""
    return db.query(AutoNotification).filter(AutoNotification.notif_auto_id == notif_auto_id).first()


def get_auto_notifications(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    usuario_id: Optional[int] = None,
    estado: Optional[AutoNotificationStatus] = None,
    cita_id: Optional[int] = None,
) -> List[AutoNotification]:
    """Get auto notifications with optional filters"""
    query = db.query(AutoNotification)
    
    if usuario_id is not None:
        query = query.filter(AutoNotification.usuario_id == usuario_id)
    if estado is not None:
        query = query.filter(AutoNotification.estado == estado)
    if cita_id is not None:
        query = query.filter(AutoNotification.cita_id == cita_id)
    
    return query.offset(skip).limit(limit).all()


def get_pending_notifications(db: Session, limit: int = 500) -> List[AutoNotification]:
    """Get all pending notifications waiting to be sent"""
    return (
        db.query(AutoNotification)
        .filter(
            AutoNotification.estado == AutoNotificationStatus.PENDING,
            AutoNotification.fecha_programada <= datetime.utcnow(),
        )
        .limit(limit)
        .all()
    )


def create_auto_notification(
    db: Session, notification: AutoNotificationCreate
) -> AutoNotification:
    """Create a new automatic notification"""
    notif_data = notification.model_dump()
    # Map 'metadata' from schema to 'metadata_json' for the model
    if "metadata" in notif_data:
        notif_data["metadata_json"] = notif_data.pop("metadata")
        
    db_notification = AutoNotification(**notif_data)
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification


def update_auto_notification(
    db: Session,
    notif_auto_id: int,
    notification: AutoNotificationUpdate,
) -> Optional[AutoNotification]:
    """Update an auto notification"""
    db_notification = get_auto_notification(db, notif_auto_id)
    if not db_notification:
        return None

    update_data = notification.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_notification, field, value)

    db.commit()
    db.refresh(db_notification)
    return db_notification


def mark_sent(
    db: Session, notif_auto_id: int, sent_at: Optional[datetime] = None
) -> Optional[AutoNotification]:
    """Mark a notification as successfully sent"""
    db_notification = get_auto_notification(db, notif_auto_id)
    if not db_notification:
        return None

    db_notification.estado = AutoNotificationStatus.SENT
    db_notification.fecha_enviada = sent_at or datetime.utcnow()
    db.commit()
    db.refresh(db_notification)
    return db_notification


def mark_failed(
    db: Session, notif_auto_id: int, error_msg: Optional[str] = None
) -> Optional[AutoNotification]:
    """Mark a notification as failed"""
    db_notification = get_auto_notification(db, notif_auto_id)
    if not db_notification:
        return None

    db_notification.estado = AutoNotificationStatus.FAILED
    db_notification.intentos += 1
    db_notification.ultimo_error = error_msg
    db.commit()
    db.refresh(db_notification)
    return db_notification


def delete_auto_notification(db: Session, notif_auto_id: int) -> bool:
    """Delete an auto notification"""
    db_notification = get_auto_notification(db, notif_auto_id)
    if not db_notification:
        return False

    db.delete(db_notification)
    db.commit()
    return True
