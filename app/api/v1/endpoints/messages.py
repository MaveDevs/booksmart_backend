from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import crud_messages, crud_appointments, crud_services, crud_establishments
from app.models import User
from app.schemas.messages import MessageCreate, MessageResponse, MessageUpdate
from app.core.permissions import (
    RoleType,
    get_user_role_name,
    require_admin,
)

router = APIRouter()


def _user_can_access_appointment_messages(db: Session, user: User, cita_id: int) -> bool:
    """Check if user can access messages for this appointment."""
    user_role = get_user_role_name(user)
    
    # Admin can access all
    if user_role == RoleType.ADMIN.value:
        return True
    
    appointment = crud_appointments.get_appointment(db, cita_id)
    if not appointment:
        return False
    
    # Client can access their own appointment's messages
    if appointment.cliente_id == user.usuario_id:
        return True
    
    # Owner can access messages for appointments at their establishment
    if user_role == RoleType.DUENO.value:
        service = crud_services.get_service(db, appointment.servicio_id)
        if service:
            establishment = crud_establishments.get_establishment(db, service.establecimiento_id)
            if establishment and establishment.usuario_id == user.usuario_id:
                return True
    
    # Worker can access messages for their assigned appointments
    from app.crud import crud_workers
    worker = crud_workers.get_worker_by_user(db, user.usuario_id)
    if worker and appointment.trabajador_id == worker.trabajador_id:
        return True
    
    return False


@router.get("/", response_model=List[MessageResponse])
def get_messages(
    cita_id: Optional[int] = Query(None),
    emisor_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    List messages.
    - Must specify cita_id to get messages
    - Users can only see messages for appointments they have access to
    """
    user_role = get_user_role_name(current_user)
    
    # Admin can see all messages
    if user_role == RoleType.ADMIN.value:
        return crud_messages.get_messages(db, skip=skip, limit=limit, cita_id=cita_id, emisor_id=emisor_id)
    
    # Other users must specify an appointment and have access to it
    if not cita_id:
        raise HTTPException(
            status_code=400,
            detail="You must specify cita_id to view messages"
        )
    
    if not _user_can_access_appointment_messages(db, current_user, cita_id):
        raise HTTPException(status_code=403, detail="You don't have access to this appointment's messages")
    
    return crud_messages.get_messages(db, skip=skip, limit=limit, cita_id=cita_id, emisor_id=emisor_id)


@router.get("/{message_id}", response_model=MessageResponse)
def get_message(
    message_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Get a specific message. Users can only view messages for appointments they have access to."""
    message = crud_messages.get_message(db, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    if not _user_can_access_appointment_messages(db, current_user, message.cita_id):
        raise HTTPException(status_code=403, detail="You don't have access to this message")
    
    return message


@router.post("/", response_model=MessageResponse)
def create_message(
    message: MessageCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Create a message in an appointment conversation.
    - emisor_id must match current user (you can only send as yourself)
    - Must have access to the appointment
    """
    # Verify user can only send messages as themselves
    if message.emisor_id != current_user.usuario_id:
        raise HTTPException(
            status_code=403,
            detail="You can only send messages as yourself"
        )
    
    # Verify user has access to this appointment
    if not _user_can_access_appointment_messages(db, current_user, message.cita_id):
        raise HTTPException(
            status_code=403,
            detail="You don't have access to this appointment"
        )
    
    try:
        return crud_messages.create_message(db, message)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{message_id}", response_model=MessageResponse)
def update_message(
    message_id: int,
    message: MessageUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Update a message. Users can only update their own messages."""
    db_message = crud_messages.get_message(db, message_id)
    if not db_message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    user_role = get_user_role_name(current_user)
    # Only the sender or admin can update a message
    if db_message.emisor_id != current_user.usuario_id and user_role != RoleType.ADMIN.value:
        raise HTTPException(status_code=403, detail="You can only update your own messages")
    
    db_message = crud_messages.update_message(db, message_id, message)
    return db_message


@router.patch("/{message_id}", response_model=MessageResponse)
def patch_message(
    message_id: int,
    message: MessageUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Partial update for a message. Same rules as PUT."""
    db_message = crud_messages.get_message(db, message_id)
    if not db_message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    user_role = get_user_role_name(current_user)
    if db_message.emisor_id != current_user.usuario_id and user_role != RoleType.ADMIN.value:
        raise HTTPException(status_code=403, detail="You can only update your own messages")
    
    db_message = crud_messages.update_message(db, message_id, message)
    return db_message


@router.delete("/{message_id}")
def delete_message(
    message_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_admin()),
):
    """Only admins can delete messages."""
    success = crud_messages.delete_message(db, message_id)
    if not success:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"message": "Message deleted successfully"}
