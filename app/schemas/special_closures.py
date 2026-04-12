from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, model_validator


class SpecialClosureBase(BaseModel):
    establecimiento_id: int
    fecha: date
    motivo: Optional[str] = None


class SpecialClosureCreate(SpecialClosureBase):
    pass


class SpecialClosureUpdate(BaseModel):
    motivo: Optional[str] = None


class SpecialClosureResponse(SpecialClosureBase):
    cierre_id: int
    creado_en: datetime

    class Config:
        from_attributes = True