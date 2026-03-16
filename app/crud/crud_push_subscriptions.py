from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.push_subscriptions import PushSubscription
from app.schemas.push_subscriptions import PushSubscriptionCreate


def get_subscriptions_by_user(db: Session, usuario_id: int) -> List[PushSubscription]:
    return (
        db.query(PushSubscription)
        .filter(PushSubscription.usuario_id == usuario_id)
        .all()
    )


def get_all_subscriptions(db: Session) -> List[PushSubscription]:
    return db.query(PushSubscription).all()


def upsert_subscription(
    db: Session, usuario_id: int, data: PushSubscriptionCreate
) -> PushSubscription:
    """Insert new subscription or update existing one for the same endpoint."""
    existing = (
        db.query(PushSubscription)
        .filter(
            PushSubscription.usuario_id == usuario_id,
            PushSubscription.endpoint == data.endpoint,
        )
        .first()
    )

    if existing:
        existing.p256dh = data.keys.p256dh
        existing.auth = data.keys.auth
        db.commit()
        db.refresh(existing)
        return existing

    subscription = PushSubscription(
        usuario_id=usuario_id,
        endpoint=data.endpoint,
        p256dh=data.keys.p256dh,
        auth=data.keys.auth,
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription


def delete_subscription(db: Session, usuario_id: int, endpoint: str) -> bool:
    sub = (
        db.query(PushSubscription)
        .filter(
            PushSubscription.usuario_id == usuario_id,
            PushSubscription.endpoint == endpoint,
        )
        .first()
    )
    if not sub:
        return False
    db.delete(sub)
    db.commit()
    return True


def delete_all_subscriptions_for_user(db: Session, usuario_id: int) -> int:
    deleted = (
        db.query(PushSubscription)
        .filter(PushSubscription.usuario_id == usuario_id)
        .delete()
    )
    db.commit()
    return deleted
