from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import crud_notifications
from app.models import User
from app.schemas.notifications import (
    NotificationCreate,
    NotificationResponse,
    NotificationUpdate,
)
from app.core.permissions import (
    RoleType,
    get_user_role_name,
    require_admin,
)
from app.services.realtime import notify_user

router = APIRouter()


@router.get("/", response_model=List[NotificationResponse])
def get_notifications(
    usuario_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    List notifications.
    - Users can only see their own notifications
    - Admins can see all notifications
    """
    user_role = get_user_role_name(current_user)
    
    # Admin can see all
    if user_role == RoleType.ADMIN.value:
        return crud_notifications.get_notifications(db, skip=skip, limit=limit, usuario_id=usuario_id)
    
    # Others can only see their own
    return crud_notifications.get_notifications(
        db, skip=skip, limit=limit, usuario_id=current_user.usuario_id
    )


@router.get("/me", response_model=List[NotificationResponse])
def get_my_notifications(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Get current user's notifications."""
    return crud_notifications.get_notifications(
        db, skip=skip, limit=limit, usuario_id=current_user.usuario_id
    )


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(
    notification_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Get a specific notification. Users can only view their own notifications."""
    notification = crud_notifications.get_notification(db, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    user_role = get_user_role_name(current_user)
    if notification.usuario_id != current_user.usuario_id and user_role != RoleType.ADMIN.value:
        raise HTTPException(status_code=403, detail="You can only view your own notifications")
    
    return notification


@router.post("/", response_model=NotificationResponse)
async def create_notification(
    notification: NotificationCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_admin()),
):
    """Only admins/system can create notifications."""
    try:
        db_notification = crud_notifications.create_notification(db, notification)
        # Push real-time notification to the target user via WebSocket
        await notify_user(db_notification.usuario_id, db_notification)
        return db_notification
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{notification_id}", response_model=NotificationResponse)
def update_notification(
    notification_id: int,
    notification: NotificationUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Update notification (e.g., mark as read). Users can only update their own notifications."""
    db_notification = crud_notifications.get_notification(db, notification_id)
    if not db_notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    user_role = get_user_role_name(current_user)
    if db_notification.usuario_id != current_user.usuario_id and user_role != RoleType.ADMIN.value:
        raise HTTPException(status_code=403, detail="You can only update your own notifications")
    
    db_notification = crud_notifications.update_notification(db, notification_id, notification)
    return db_notification


@router.patch("/{notification_id}", response_model=NotificationResponse)
def patch_notification(
    notification_id: int,
    notification: NotificationUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Partial update for notification (e.g., mark as read). Same rules as PUT."""
    db_notification = crud_notifications.get_notification(db, notification_id)
    if not db_notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    user_role = get_user_role_name(current_user)
    if db_notification.usuario_id != current_user.usuario_id and user_role != RoleType.ADMIN.value:
        raise HTTPException(status_code=403, detail="You can only update your own notifications")
    
    db_notification = crud_notifications.update_notification(db, notification_id, notification)
    return db_notification


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_admin()),
):
    """Only admins can delete notifications."""
    success = crud_notifications.delete_notification(db, notification_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification deleted successfully"}
