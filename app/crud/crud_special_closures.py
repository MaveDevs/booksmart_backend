from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Establishment, SpecialClosure
from app.schemas.special_closures import SpecialClosureCreate, SpecialClosureUpdate


def get_closure(db: Session, closure_id: int) -> Optional[SpecialClosure]:
    return db.query(SpecialClosure).filter(SpecialClosure.cierre_id == closure_id).first()


def get_closures(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    establecimiento_id: Optional[int] = None,
) -> List[SpecialClosure]:
    query = db.query(SpecialClosure)
    if establecimiento_id is not None:
        query = query.filter(SpecialClosure.establecimiento_id == establecimiento_id)
    return query.order_by(SpecialClosure.fecha.desc()).offset(skip).limit(limit).all()


def get_closure_by_date(db: Session, establishment_id: int, closure_date) -> Optional[SpecialClosure]:
    return (
        db.query(SpecialClosure)
        .filter(
            SpecialClosure.establecimiento_id == establishment_id,
            SpecialClosure.fecha == closure_date,
        )
        .first()
    )


def create_closure(db: Session, closure: SpecialClosureCreate) -> SpecialClosure:
    establishment = (
        db.query(Establishment)
        .filter(Establishment.establecimiento_id == closure.establecimiento_id)
        .first()
    )
    if not establishment:
        raise ValueError(f"Establishment with id {closure.establecimiento_id} does not exist")

    db_closure = SpecialClosure(**closure.model_dump())
    db.add(db_closure)
    db.commit()
    db.refresh(db_closure)
    return db_closure


def update_closure(db: Session, closure_id: int, closure: SpecialClosureUpdate) -> Optional[SpecialClosure]:
    db_closure = get_closure(db, closure_id)
    if not db_closure:
        return None

    update_data = closure.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_closure, field, value)

    db.commit()
    db.refresh(db_closure)
    return db_closure


def delete_closure(db: Session, closure_id: int) -> bool:
    db_closure = get_closure(db, closure_id)
    if not db_closure:
        return False

    db.delete(db_closure)
    db.commit()
    return True