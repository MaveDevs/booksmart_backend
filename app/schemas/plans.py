from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class PlanBase(BaseModel):
	nombre: str = Field(..., min_length=1, max_length=50)
	descripcion: Optional[str] = None
	precio: Decimal = Field(..., ge=0)
	activo: bool = True


class PlanCreate(PlanBase):
	pass


class PlanUpdate(BaseModel):
	nombre: Optional[str] = Field(None, min_length=1, max_length=50)
	descripcion: Optional[str] = None
	precio: Optional[Decimal] = Field(None, ge=0)
	activo: Optional[bool] = None


class PlanResponse(PlanBase):
	plan_id: int

	class Config:
		from_attributes = True

