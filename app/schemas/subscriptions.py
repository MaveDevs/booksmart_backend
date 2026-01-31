import enum
from datetime import date
from typing import Optional

from pydantic import BaseModel, model_validator


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

	@model_validator(mode="after")
	def validate_dates(self) -> "SubscriptionBase":
		if self.fecha_fin is not None and self.fecha_fin <= self.fecha_inicio:
			raise ValueError("fecha_fin must be after fecha_inicio")
		return self


class SubscriptionCreate(SubscriptionBase):
	pass


class SubscriptionUpdate(BaseModel):
	establecimiento_id: Optional[int] = None
	plan_id: Optional[int] = None
	fecha_inicio: Optional[date] = None
	fecha_fin: Optional[date] = None
	estado: Optional[SubscriptionStatus] = None

	@model_validator(mode="after")
	def validate_dates(self) -> "SubscriptionUpdate":
		if self.fecha_inicio is not None and self.fecha_fin is not None:
			if self.fecha_fin <= self.fecha_inicio:
				raise ValueError("fecha_fin must be after fecha_inicio")
		return self


class SubscriptionResponse(SubscriptionBase):
	suscripcion_id: int

	class Config:
		from_attributes = True

