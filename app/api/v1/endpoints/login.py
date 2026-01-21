from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.core import security
from app.crud import crud_users
from app.schemas.token import Token
from app.schemas.login import LoginRequest

router = APIRouter()

@router.post("/login/access-token", response_model=Token)
def login_access_token(login_data: LoginRequest, db: Session = Depends(deps.get_db)) -> Any:
    user = crud_users.get_user_by_email(db, email=login_data.email)
    
    if not user or not security.verify_password(login_data.password, str(user.contrasena_hash)):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    if not bool(user.activo):
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(subject=user.usuario_id, expires_delta=access_token_expires),
        "token_type": "bearer",
    }