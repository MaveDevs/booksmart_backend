from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import crud_payments, crud_subscriptions, crud_establishments
from app.models import User
from app.schemas.payments import PaymentCreate, PaymentResponse, PaymentUpdate
from app.core.permissions import (
    RoleType,
    get_user_role_name,
    require_admin,
    require_owner_or_admin,
)

router = APIRouter()


def _user_can_access_payment(db: Session, user: User, payment) -> bool:
    """Check if user can access this payment."""
    user_role = get_user_role_name(user)
    
    # Admin can access all
    if user_role == RoleType.ADMIN.value:
        return True
    
    # Owner can only access payments for their establishments' subscriptions
    if user_role == RoleType.DUENO.value:
        subscription = crud_subscriptions.get_subscription(db, payment.suscripcion_id)
        if subscription:
            establishment = crud_establishments.get_establishment(db, subscription.establecimiento_id)
            if establishment and establishment.usuario_id == user.usuario_id:
                return True
    
    return False


@router.get("/", response_model=List[PaymentResponse])
def get_payments(
    suscripcion_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_owner_or_admin()),
):
    """
    List payments. Owners can only see payments for their establishments' subscriptions.
    Admins can see all payments.
    """
    user_role = get_user_role_name(current_user)
    
    # Admin can see all
    if user_role == RoleType.ADMIN.value:
        return crud_payments.get_payments(db, skip=skip, limit=limit, suscripcion_id=suscripcion_id)
    
    # Owner: filter by their establishments' subscriptions
    if suscripcion_id:
        subscription = crud_subscriptions.get_subscription(db, suscripcion_id)
        if subscription:
            establishment = crud_establishments.get_establishment(db, subscription.establecimiento_id)
            if not establishment or establishment.usuario_id != current_user.usuario_id:
                raise HTTPException(status_code=403, detail="You don't own this subscription's establishment")
        return crud_payments.get_payments(db, skip=skip, limit=limit, suscripcion_id=suscripcion_id)
    
    # Get payments for all owner's establishments' subscriptions
    establishments = crud_establishments.get_establishments_by_user(db, current_user.usuario_id)
    all_payments = []
    for est in establishments:
        subs = crud_subscriptions.get_subscriptions(db, establecimiento_id=est.establecimiento_id)
        for sub in subs:
            payments = crud_payments.get_payments(db, suscripcion_id=sub.suscripcion_id)
            all_payments.extend(payments)
    return all_payments[skip:skip + limit]


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_owner_or_admin()),
):
    """Get a specific payment. Owners can only view payments for their establishments' subscriptions."""
    payment = crud_payments.get_payment(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if not _user_can_access_payment(db, current_user, payment):
        raise HTTPException(status_code=403, detail="You don't have access to this payment")
    
    return payment


@router.post("/", response_model=PaymentResponse)
def create_payment(
    payment: PaymentCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_admin()),
):
    """Only admins/payment system can create payments."""
    try:
        return crud_payments.create_payment(db, payment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{payment_id}", response_model=PaymentResponse)
def update_payment(
    payment_id: int,
    payment: PaymentUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_admin()),
):
    """Only admins can update payments."""
    db_payment = crud_payments.update_payment(db, payment_id, payment)
    if not db_payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return db_payment


@router.patch("/{payment_id}", response_model=PaymentResponse)
def patch_payment(
    payment_id: int,
    payment: PaymentUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_admin()),
):
    """Only admins can patch payments."""
    db_payment = crud_payments.update_payment(db, payment_id, payment)
    if not db_payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return db_payment


@router.delete("/{payment_id}")
def delete_payment(
    payment_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_admin()),
):
    """Only admins can delete payments."""
    success = crud_payments.delete_payment(db, payment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"message": "Payment deleted successfully"}
