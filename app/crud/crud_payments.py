from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Payment, Subscription
from app.schemas.payments import PaymentCreate, PaymentUpdate


def get_payment(db: Session, payment_id: int) -> Optional[Payment]:
    return db.query(Payment).filter(Payment.pago_id == payment_id).first()


def get_payments(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    suscripcion_id: Optional[int] = None,
) -> List[Payment]:
    query = db.query(Payment)
    if suscripcion_id is not None:
        query = query.filter(Payment.suscripcion_id == suscripcion_id)
    return query.offset(skip).limit(limit).all()


def create_payment(db: Session, payment: PaymentCreate) -> Payment:
    # Verify suscripcion_id exists
    subscription = (
        db.query(Subscription)
        .filter(Subscription.suscripcion_id == payment.suscripcion_id)
        .first()
    )
    if not subscription:
        raise ValueError(f"Subscription with id {payment.suscripcion_id} does not exist")
    
    payment_data = payment.model_dump()
    db_payment = Payment(**payment_data)  # type: ignore[arg-type]
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment


def update_payment(db: Session, payment_id: int, payment: PaymentUpdate) -> Optional[Payment]:
    db_payment = get_payment(db, payment_id)
    if not db_payment:
        return None

    update_data = payment.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_payment, field, value)

    db.commit()
    db.refresh(db_payment)
    return db_payment


def delete_payment(db: Session, payment_id: int) -> bool:
    db_payment = get_payment(db, payment_id)
    if not db_payment:
        return False

    db.delete(db_payment)
    db.commit()
    return True
