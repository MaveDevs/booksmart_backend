import re
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class EstablishmentBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = None
    direccion: Optional[str] = Field(None, max_length=255)
    latitud: Optional[float] = Field(None, ge=-90, le=90)
    longitud: Optional[float] = Field(None, ge=-180, le=180)
    telefono: Optional[str] = Field(None, max_length=20)
    usuario_id: int
    activo: bool = True

    @field_validator("telefono")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # Allow digits, spaces, dashes, parentheses, and plus sign
        if not re.match(r"^[\d\s\-\(\)\+]+$", v):
            raise ValueError("Invalid phone number format")
        return v


class EstablishmentCreate(EstablishmentBase):
    pass


class EstablishmentUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = None
    direccion: Optional[str] = Field(None, max_length=255)
    latitud: Optional[float] = Field(None, ge=-90, le=90)
    longitud: Optional[float] = Field(None, ge=-180, le=180)
    telefono: Optional[str] = Field(None, max_length=20)
    activo: Optional[bool] = None

    @field_validator("telefono")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not re.match(r"^[\d\s\-\(\)\+]+$", v):
            raise ValueError("Invalid phone number format")
        return v


class EstablishmentResponse(EstablishmentBase):
    establecimiento_id: int

    class Config:
        from_attributes = True


class NearbyEstablishmentResponse(EstablishmentResponse):
    distance_km: float
    ranking_score: float
    subscription_active: bool = False
    subscription_plan_id: Optional[int] = None
    subscription_plan_name: Optional[str] = None

    class Config:
        from_attributes = True
