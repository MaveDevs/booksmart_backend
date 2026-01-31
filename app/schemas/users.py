import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


# Toggle for password validation - set to True for production
ENABLE_PASSWORD_VALIDATION = False


def validate_password_strength(password: str) -> str:
    """Validate password meets security requirements."""
    if not ENABLE_PASSWORD_VALIDATION:
        return password
    
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter")
    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least one digit")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValueError("Password must contain at least one special character")
    return password


class UserBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)
    apellido: str = Field(..., min_length=1, max_length=50)
    correo: EmailStr = Field(..., max_length=100)
    rol_id: Optional[int] = None
    activo: bool = True


class UserCreate(UserBase):
    contrasena: str = Field(..., min_length=1)

    @field_validator("contrasena")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return validate_password_strength(v)


class UserUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=50)
    apellido: Optional[str] = Field(None, min_length=1, max_length=50)
    correo: Optional[EmailStr] = None
    contrasena: Optional[str] = None
    rol_id: Optional[int] = None
    activo: Optional[bool] = None

    @field_validator("contrasena")
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_password_strength(v)


class UserResponse(UserBase):
    usuario_id: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True