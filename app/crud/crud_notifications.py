from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Notification, User
from app.schemas.notifications import NotificationCreate, NotificationUpdate


def get_notification(db: Session, notification_id: int) -> Optional[Notification]:
    return db.query(Notification).filter(Notification.notificacion_id == notification_id).first()


def get_notifications(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    usuario_id: Optional[int] = None,
) -> List[Notification]:
    query = db.query(Notification)
    if usuario_id is not None:
        query = query.filter(Notification.usuario_id == usuario_id)
    return query.offset(skip).limit(limit).all()


def create_notification(db: Session, notification: NotificationCreate) -> Notification:
    # Verify usuario_id exists
    user = db.query(User).filter(User.usuario_id == notification.usuario_id).first()
    if not user:
        raise ValueError(f"User with id {notification.usuario_id} does not exist")
    
    notification_data = notification.model_dump()
    db_notification = Notification(**notification_data)  # type: ignore[arg-type]
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification


def update_notification(
    db: Session,
    notification_id: int,
    notification: NotificationUpdate,
) -> Optional[Notification]:
    db_notification = get_notification(db, notification_id)
    if not db_notification:
        return None

    update_data = notification.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_notification, field, value)

    db.commit()
    db.refresh(db_notification)
    return db_notification


def delete_notification(db: Session, notification_id: int) -> bool:
    db_notification = get_notification(db, notification_id)
    if not db_notification:
        return False

    db.delete(db_notification)
    db.commit()
    return True
