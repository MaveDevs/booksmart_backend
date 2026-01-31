from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Establishment, Plan, Subscription
from app.schemas.subscriptions import SubscriptionCreate, SubscriptionUpdate


def get_subscription(db: Session, subscription_id: int) -> Optional[Subscription]:
    return db.query(Subscription).filter(Subscription.suscripcion_id == subscription_id).first()


def get_subscriptions(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    establecimiento_id: Optional[int] = None,
    plan_id: Optional[int] = None,
) -> List[Subscription]:
    query = db.query(Subscription)
    if establecimiento_id is not None:
        query = query.filter(Subscription.establecimiento_id == establecimiento_id)
    if plan_id is not None:
        query = query.filter(Subscription.plan_id == plan_id)
    return query.offset(skip).limit(limit).all()


def create_subscription(db: Session, subscription: SubscriptionCreate) -> Subscription:
    # Verify establecimiento_id exists
    establishment = (
        db.query(Establishment)
        .filter(Establishment.establecimiento_id == subscription.establecimiento_id)
        .first()
    )
    if not establishment:
        raise ValueError(f"Establishment with id {subscription.establecimiento_id} does not exist")
    
    # Verify plan_id exists
    plan = db.query(Plan).filter(Plan.plan_id == subscription.plan_id).first()
    if not plan:
        raise ValueError(f"Plan with id {subscription.plan_id} does not exist")
    
    subscription_data = subscription.model_dump()
    db_subscription = Subscription(**subscription_data)  # type: ignore[arg-type]
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription


def update_subscription(
    db: Session,
    subscription_id: int,
    subscription: SubscriptionUpdate,
) -> Optional[Subscription]:
    db_subscription = get_subscription(db, subscription_id)
    if not db_subscription:
        return None

    update_data = subscription.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_subscription, field, value)

    db.commit()
    db.refresh(db_subscription)
    return db_subscription


def delete_subscription(db: Session, subscription_id: int) -> bool:
    db_subscription = get_subscription(db, subscription_id)
    if not db_subscription:
        return False

    db.delete(db_subscription)
    db.commit()
    return True
