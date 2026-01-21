import enum

from datetime import date
from typing import Optional

from pydantic import BaseModel


class SubscriptionStatus(str, enum.Enum):
	ACTIVA = "ACTIVA"
	CANCELADA = "CANCELADA"
	EXPIRADA = "EXPIRADA"


class SubscriptionBase(BaseModel):
	establecimiento_id: int
	plan_id: int
	fecha_inicio: date
	fecha_fin: Optional[date] = None
	estado: SubscriptionStatus = SubscriptionStatus.ACTIVA
	auto_renovacion: bool = True


class SubscriptionCreate(SubscriptionBase):
	pass


class SubscriptionResponse(SubscriptionBase):
	suscripcion_id: int

	class Config:
		from_attributes = True

