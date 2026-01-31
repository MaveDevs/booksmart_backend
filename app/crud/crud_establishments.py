from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Establishment, User
from app.schemas.establishments import EstablishmentCreate, EstablishmentUpdate


def get_establishment(db: Session, establishment_id: int) -> Optional[Establishment]:
    return (
        db.query(Establishment)
        .filter(Establishment.establecimiento_id == establishment_id)
        .first()
    )


def get_establishments(db: Session, skip: int = 0, limit: int = 100) -> List[Establishment]:
    return db.query(Establishment).offset(skip).limit(limit).all()


def get_establishments_by_user(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[Establishment]:
    return (
        db.query(Establishment)
        .filter(Establishment.usuario_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_establishment(db: Session, establishment: EstablishmentCreate) -> Establishment:
    # Verify usuario_id exists
    user = db.query(User).filter(User.usuario_id == establishment.usuario_id).first()
    if not user:
        raise ValueError(f"User with id {establishment.usuario_id} does not exist")
    
    db_establishment = Establishment(**establishment.model_dump())
    db.add(db_establishment)
    db.commit()
    db.refresh(db_establishment)
    return db_establishment

def update_establishment(db: Session, establishment_id: int, establishment: EstablishmentUpdate) -> Optional[Establishment]:
    db_establishment = get_establishment(db, establishment_id)
    if not db_establishment:
        return None
    
    update_data = establishment.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_establishment, field, value)
    
    db.commit()
    db.refresh(db_establishment)
    return db_establishment

def delete_establishment(db: Session, establishment_id: int) -> bool:
    db_establishment = get_establishment(db, establishment_id)
    if not db_establishment:
        return False
    
    db.delete(db_establishment)
    db.commit()
    return True