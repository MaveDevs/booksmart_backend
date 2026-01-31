from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class ServiceBase(BaseModel):
    establecimiento_id: int
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = None
    duracion: int = Field(..., gt=0, description="Duration in minutes")
    precio: Decimal = Field(..., ge=0)
    activo: bool = True


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    establecimiento_id: Optional[int] = None
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = None
    duracion: Optional[int] = Field(None, gt=0)
    precio: Optional[Decimal] = Field(None, ge=0)
    activo: Optional[bool] = None


class ServiceResponse(ServiceBase):
    servicio_id: int

    class Config:
        from_attributes = True