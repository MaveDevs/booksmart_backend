import os
from datetime import datetime
from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.security import ALGORITHM, SECRET_KEY
from app.crud import crud_users
from app.db.session import SessionLocal
from app.models import User

reusable_oauth2 = HTTPBearer(auto_error=False)


def _is_jwt_auth_disabled() -> bool:
    return os.getenv("JWT_AUTH_DISABLED", "false").lower() == "true"


def _get_bypass_user_id() -> int:
    raw_user_id = os.getenv("JWT_BYPASS_USER_ID", "1")
    try:
        return int(raw_user_id)
    except ValueError:
        return 1


def _build_bypass_user() -> User:
    raw_role_id = os.getenv("JWT_BYPASS_ROLE_ID", "3")
    try:
        bypass_role_id = int(raw_role_id)
    except ValueError:
        bypass_role_id = 3

    bypass_user = User(
        usuario_id=_get_bypass_user_id(),
        nombre=os.getenv("JWT_BYPASS_NAME", "Bypass"),
        apellido=os.getenv("JWT_BYPASS_LASTNAME", "User"),
        correo=os.getenv("JWT_BYPASS_EMAIL", "bypass@booksmart.com"),
        contrasena_hash="bypass",
        rol_id=bypass_role_id,
        activo=True,
        fecha_creacion=datetime.utcnow(),
    )
    return bypass_user

def get_db() -> Generator:
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        if db is not None:
            db.close()


def get_current_user(
    db: Session = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(reusable_oauth2),
) -> User:
    if _is_jwt_auth_disabled():
        return _build_bypass_user()

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise credentials_exception

    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        subject = payload.get("sub")
        if subject is None:
            raise credentials_exception
        user_id = int(subject)
    except (JWTError, ValueError):
        raise credentials_exception

    user = crud_users.get_user(db, user_id=user_id)
    if not user:
        raise credentials_exception
    if not bool(user.activo):
        raise HTTPException(status_code=400, detail="Inactive user")
    return user