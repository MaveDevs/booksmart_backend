from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import crud_subscriptions, crud_establishments
from app.models import User
from app.schemas.subscriptions import (
    SubscriptionCreate,
    SubscriptionResponse,
    SubscriptionUpdate,
)
from app.core.permissions import (
    RoleType,
    get_user_role_name,
    require_admin,
    require_owner_or_admin,
)

router = APIRouter()


def _user_can_access_subscription(db: Session, user: User, subscription) -> bool:
    """Check if user can access this subscription."""
    user_role = get_user_role_name(user)
    
    # Admin can access all
    if user_role == RoleType.ADMIN.value:
        return True
    
    # Owner can only access subscriptions for their establishments
    if user_role == RoleType.DUENO.value:
        establishment = crud_establishments.get_establishment(db, subscription.establecimiento_id)
        if establishment and establishment.usuario_id == user.usuario_id:
            return True
    
    return False


@router.get("/", response_model=List[SubscriptionResponse])
def get_subscriptions(
    establecimiento_id: Optional[int] = Query(None),
    plan_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_owner_or_admin()),
):
    """
    List subscriptions. Owners can only see subscriptions for their establishments.
    Admins can see all subscriptions.
    """
    user_role = get_user_role_name(current_user)
    
    # Admin can see all
    if user_role == RoleType.ADMIN.value:
        return crud_subscriptions.get_subscriptions(
            db, skip=skip, limit=limit, establecimiento_id=establecimiento_id, plan_id=plan_id
        )
    
    # Owner: filter by their establishments
    if establecimiento_id:
        establishment = crud_establishments.get_establishment(db, establecimiento_id)
        if not establishment or establishment.usuario_id != current_user.usuario_id:
            raise HTTPException(status_code=403, detail="You don't own this establishment")
        return crud_subscriptions.get_subscriptions(
            db, skip=skip, limit=limit, establecimiento_id=establecimiento_id, plan_id=plan_id
        )
    
    # Get subscriptions for all owner's establishments
    establishments = crud_establishments.get_establishments_by_user(db, current_user.usuario_id)
    all_subscriptions = []
    for est in establishments:
        subs = crud_subscriptions.get_subscriptions(db, establecimiento_id=est.establecimiento_id, plan_id=plan_id)
        all_subscriptions.extend(subs)
    return all_subscriptions[skip:skip + limit]


@router.get("/{subscription_id}", response_model=SubscriptionResponse)
def get_subscription(
    subscription_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_owner_or_admin()),
):
    """Get a specific subscription. Owners can only view subscriptions for their establishments."""
    subscription = crud_subscriptions.get_subscription(db, subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    if not _user_can_access_subscription(db, current_user, subscription):
        raise HTTPException(status_code=403, detail="You don't have access to this subscription")
    
    return subscription


@router.post("/", response_model=SubscriptionResponse)
def create_subscription(
    subscription: SubscriptionCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_owner_or_admin()),
):
    """
    Create a subscription. Owners can only create subscriptions for their own establishments.
    """
    user_role = get_user_role_name(current_user)
    
    # Owner can only create for their own establishment
    if user_role == RoleType.DUENO.value:
        establishment = crud_establishments.get_establishment(db, subscription.establecimiento_id)
        if not establishment or establishment.usuario_id != current_user.usuario_id:
            raise HTTPException(status_code=403, detail="You can only create subscriptions for your own establishments")
    
    try:
        return crud_subscriptions.create_subscription(db, subscription)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{subscription_id}", response_model=SubscriptionResponse)
def update_subscription(
    subscription_id: int,
    subscription: SubscriptionUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_admin()),
):
    """Only admins can update subscriptions."""
    db_subscription = crud_subscriptions.update_subscription(db, subscription_id, subscription)
    if not db_subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return db_subscription


@router.patch("/{subscription_id}", response_model=SubscriptionResponse)
def patch_subscription(
    subscription_id: int,
    subscription: SubscriptionUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_admin()),
):
    """Only admins can patch subscriptions."""
    db_subscription = crud_subscriptions.update_subscription(db, subscription_id, subscription)
    if not db_subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return db_subscription


@router.delete("/{subscription_id}")
def delete_subscription(
    subscription_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_admin()),
):
    """Only admins can delete subscriptions."""
    success = crud_subscriptions.delete_subscription(db, subscription_id)
    if not success:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return {"message": "Subscription deleted successfully"}
