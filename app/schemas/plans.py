from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class PlanBase(BaseModel):
	nombre: str
	descripcion: Optional[str] = None
	precio_mensual: Decimal
	max_servicios: int = 10
	max_trabajadores: int = 5
	max_citas_mes: int = 100
	activo: bool = True


class PlanCreate(PlanBase):
	pass


class PlanResponse(PlanBase):
	plan_id: int

	class Config:
		from_attributes = True

