from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Role
from app.schemas.rol import RoleCreate, RoleUpdate


def get_role(db: Session, role_id: int) -> Optional[Role]:
    return db.query(Role).filter(Role.rol_id == role_id).first()


def get_roles(db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
    return db.query(Role).offset(skip).limit(limit).all()


def create_role(db: Session, role: RoleCreate) -> Role:
    role_data = role.model_dump()
    db_role = Role(**role_data)  # type: ignore[arg-type]
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def update_role(db: Session, role_id: int, role: RoleUpdate) -> Optional[Role]:
    db_role = get_role(db, role_id)
    if not db_role:
        return None

    update_data = role.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_role, field, value)

    db.commit()
    db.refresh(db_role)
    return db_role


def delete_role(db: Session, role_id: int) -> bool:
    db_role = get_role(db, role_id)
    if not db_role:
        return False

    db.delete(db_role)
    db.commit()
    return True
