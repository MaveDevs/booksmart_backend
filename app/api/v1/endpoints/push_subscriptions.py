from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import crud_push_subscriptions
from app.models import User
from app.schemas.push_subscriptions import (
    PushSubscriptionCreate,
    PushSubscriptionResponse,
    SendPushRequest,
)
from app.services.push_sender import send_push
from app.core.permissions import require_admin

router = APIRouter()


@router.post("/", response_model=PushSubscriptionResponse, status_code=status.HTTP_201_CREATED)
def register_subscription(
    data: PushSubscriptionCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Register or update the push subscription for the authenticated user."""
    subscription = crud_push_subscriptions.upsert_subscription(
        db=db, usuario_id=current_user.usuario_id, data=data
    )
    return subscription


@router.get("/", response_model=List[PushSubscriptionResponse])
def list_my_subscriptions(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """List all active push subscriptions for the current user."""
    return crud_push_subscriptions.get_subscriptions_by_user(
        db=db, usuario_id=current_user.usuario_id
    )


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def unsubscribe(
    endpoint: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Remove a specific push subscription (called on logout)."""
    deleted = crud_push_subscriptions.delete_subscription(
        db=db, usuario_id=current_user.usuario_id, endpoint=endpoint
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Subscription not found")


@router.post("/send/", status_code=status.HTTP_200_OK)
def send_push_to_user(
    body: SendPushRequest,
    db: Session = Depends(deps.get_db),
    _: User = Depends(require_admin()),
):
    """
    Admin-only: send a push notification to all devices of a specific user.
    Automatically removes expired subscriptions (410/404 from push service).
    """
    subscriptions = crud_push_subscriptions.get_subscriptions_by_user(
        db=db, usuario_id=body.usuario_id
    )
    if not subscriptions:
        raise HTTPException(
            status_code=404,
            detail=f"No active push subscriptions for user {body.usuario_id}",
        )

    sent = 0
    for sub in subscriptions:
        try:
            still_valid = send_push(
                endpoint=sub.endpoint,
                p256dh=sub.p256dh,
                auth=sub.auth,
                title=body.title,
                body=body.body,
                url=body.url or "/app/home",
            )
            if still_valid:
                sent += 1
            else:
                # Subscription expired — clean up
                crud_push_subscriptions.delete_subscription(
                    db=db, usuario_id=body.usuario_id, endpoint=sub.endpoint
                )
        except Exception:
            pass  # Log already emitted in push_sender; continue to next device

    return {"sent": sent, "total": len(subscriptions)}
