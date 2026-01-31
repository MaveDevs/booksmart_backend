from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Appointment, Message, User
from app.schemas.messages import MessageCreate, MessageUpdate


def get_message(db: Session, message_id: int) -> Optional[Message]:
    return db.query(Message).filter(Message.mensaje_id == message_id).first()


def get_messages(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    cita_id: Optional[int] = None,
    emisor_id: Optional[int] = None,
) -> List[Message]:
    query = db.query(Message)
    if cita_id is not None:
        query = query.filter(Message.cita_id == cita_id)
    if emisor_id is not None:
        query = query.filter(Message.emisor_id == emisor_id)
    return query.offset(skip).limit(limit).all()


def create_message(db: Session, message: MessageCreate) -> Message:
    # Verify cita_id exists
    appointment = db.query(Appointment).filter(Appointment.cita_id == message.cita_id).first()
    if not appointment:
        raise ValueError(f"Appointment with id {message.cita_id} does not exist")
    
    # Verify emisor_id exists
    sender = db.query(User).filter(User.usuario_id == message.emisor_id).first()
    if not sender:
        raise ValueError(f"User with id {message.emisor_id} does not exist")
    
    message_data = message.model_dump()
    db_message = Message(**message_data)  # type: ignore[arg-type]
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def update_message(db: Session, message_id: int, message: MessageUpdate) -> Optional[Message]:
    db_message = get_message(db, message_id)
    if not db_message:
        return None

    update_data = message.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_message, field, value)

    db.commit()
    db.refresh(db_message)
    return db_message


def delete_message(db: Session, message_id: int) -> bool:
    db_message = get_message(db, message_id)
    if not db_message:
        return False

    db.delete(db_message)
    db.commit()
    return True
