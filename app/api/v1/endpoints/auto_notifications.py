"""
Automatic Notifications Admin/Owner Endpoints

Allows:
- Admins: View and manage all auto notifications
- Owners: View auto notifications for their establishments
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import crud_auto_notifications
from app.models import User
from app.models.auto_notifications import AutoNotificationStatus
from app.schemas.auto_notifications import AutoNotificationCreate, AutoNotificationResponse, AutoNotificationUpdate
from app.core.permissions import RoleType, get_user_role_name, require_admin, require_owner_or_admin
from app.tasks.notification_worker import process_pending_notifications_once

router = APIRouter()


@router.get("/", response_model=List[AutoNotificationResponse])
def list_auto_notifications(
    usuario_id: Optional[int] = Query(None),
    estado: Optional[AutoNotificationStatus] = Query(None),
    cita_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_owner_or_admin()),
):
    """
    List auto notifications.
    - Admins can see all
    - Owners can see notifications for their establishments
    """
    user_role = get_user_role_name(current_user)

    if user_role == RoleType.ADMIN.value:
        return crud_auto_notifications.get_auto_notifications(
            db, skip=skip, limit=limit, usuario_id=usuario_id, estado=estado, cita_id=cita_id
        )

    # Owners would need to filter by their establishments
    # For now, return empty to prevent unauthorized access
    raise HTTPException(status_code=403, detail="Owners cannot list global notifications yet")


@router.get("/{notif_auto_id}", response_model=AutoNotificationResponse)
def get_auto_notification(
    notif_auto_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_admin()),
):
    """Admin: Get a specific auto notification."""
    notification = crud_auto_notifications.get_auto_notification(db, notif_auto_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Auto notification not found")
    return notification


@router.post("/", response_model=AutoNotificationResponse)
def create_auto_notification(
    notification: AutoNotificationCreate,
    db: Session = Depends(deps.get_db),
    _: User = Depends(require_admin()),
):
    """Admin: Create an auto notification."""
    try:
        return crud_auto_notifications.create_auto_notification(db, notification)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{notif_auto_id}", response_model=AutoNotificationResponse)
def update_auto_notification(
    notif_auto_id: int,
    notification: AutoNotificationUpdate,
    db: Session = Depends(deps.get_db),
    _: User = Depends(require_admin()),
):
    """Admin: Update an auto notification."""
    db_notification = crud_auto_notifications.update_auto_notification(
        db, notif_auto_id, notification
    )
    if not db_notification:
        raise HTTPException(status_code=404, detail="Auto notification not found")
    return db_notification


@router.patch("/{notif_auto_id}", response_model=AutoNotificationResponse)
def patch_auto_notification(
    notif_auto_id: int,
    notification: AutoNotificationUpdate,
    db: Session = Depends(deps.get_db),
    _: User = Depends(require_admin()),
):
    """Admin: Partially update an auto notification."""
    db_notification = crud_auto_notifications.update_auto_notification(
        db, notif_auto_id, notification
    )
    if not db_notification:
        raise HTTPException(status_code=404, detail="Auto notification not found")
    return db_notification


@router.delete("/{notif_auto_id}")
def delete_auto_notification(
    notif_auto_id: int,
    db: Session = Depends(deps.get_db),
    _: User = Depends(require_admin()),
):
    """Admin: Delete an auto notification."""
    success = crud_auto_notifications.delete_auto_notification(db, notif_auto_id)
    if not success:
        raise HTTPException(status_code=404, detail="Auto notification not found")
    return {"message": "Auto notification deleted successfully"}


@router.post("/{notif_auto_id}/mark-sent")
def mark_as_sent(
    notif_auto_id: int,
    db: Session = Depends(deps.get_db),
    _: User = Depends(require_admin()),
):
    """Admin: Mark auto notification as sent."""
    notification = crud_auto_notifications.mark_sent(db, notif_auto_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Auto notification not found")
    return {"message": "Marked as sent", "notification": AutoNotificationResponse.from_orm(notification)}


@router.post("/{notif_auto_id}/mark-failed")
def mark_as_failed(
    notif_auto_id: int,
    error_msg: Optional[str] = Query(None),
    db: Session = Depends(deps.get_db),
    _: User = Depends(require_admin()),
):
    """Admin: Mark auto notification as failed."""
    notification = crud_auto_notifications.mark_failed(db, notif_auto_id, error_msg)
    if not notification:
        raise HTTPException(status_code=404, detail="Auto notification not found")
    return {"message": "Marked as failed", "notification": AutoNotificationResponse.from_orm(notification)}


@router.get("/pending/for-delivery")
def get_pending_notifications(
    limit: int = 500,
    db: Session = Depends(deps.get_db),
    _: User = Depends(require_admin()),
):
    """
    Admin: Get pending notifications ready for delivery.
    Used by background workers to send scheduled notifications.
    """
    notifications = crud_auto_notifications.get_pending_notifications(db, limit=limit)
    return [AutoNotificationResponse.from_orm(n) for n in notifications]


@router.post("/pending/process-now")
async def process_pending_notifications_now(
    limit: int = 200,
    _: User = Depends(require_admin()),
):
    """
    Admin: Process pending notifications immediately.
    Useful for manual runs or smoke checks without waiting for worker schedule.
    """
    return await process_pending_notifications_once(limit=limit)
