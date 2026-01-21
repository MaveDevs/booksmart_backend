from sqlalchemy.orm import Session
from typing import Optional, List
from app.models import User, Role
from app.schemas.users import UserCreate, UserUpdate
from app.core.security import get_password_hash

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.usuario_id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.correo == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate) -> User:
    # Verify role exists when provided
    if user.rol_id is not None:
        role = db.query(Role).filter(Role.rol_id == user.rol_id).first()
        if not role:
            raise ValueError(f"Role with id {user.rol_id} does not exist")
    
    user_data = user.model_dump()
    user_data["contrasena_hash"] = get_password_hash(user_data.pop("contrasena"))
    db_user = User(**user_data)  # type: ignore[arg-type]
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user: UserUpdate) -> Optional[User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user.model_dump(exclude_unset=True)
    
    # Verify role exists if being updated
    if "rol_id" in update_data and update_data["rol_id"] is not None:
        role = db.query(Role).filter(Role.rol_id == update_data["rol_id"]).first()
        if not role:
            raise ValueError(f"Role with id {update_data['rol_id']} does not exist")
    
    # Handle password separately
    if "contrasena" in update_data and update_data["contrasena"] is not None:
        update_data["contrasena_hash"] = get_password_hash(update_data.pop("contrasena"))
    elif "contrasena" in update_data:
        update_data.pop("contrasena")
    
    # Remove None values to prevent overwriting with null
    update_data = {k: v for k, v in update_data.items() if v is not None}
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True