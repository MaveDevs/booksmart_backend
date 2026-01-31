import enum
from datetime import date, datetime, time
from typing import Optional

from pydantic import BaseModel, model_validator


class AppointmentStatus(str, enum.Enum):
	PENDIENTE = "PENDIENTE"
	CONFIRMADA = "CONFIRMADA"
	CANCELADA = "CANCELADA"
	COMPLETADA = "COMPLETADA"


class AppointmentBase(BaseModel):
	cliente_id: int
	servicio_id: int
	fecha: date
	hora_inicio: time
	hora_fin: time
	estado: AppointmentStatus = AppointmentStatus.PENDIENTE

	@model_validator(mode="after")
	def validate_times(self) -> "AppointmentBase":
		if self.hora_fin <= self.hora_inicio:
			raise ValueError("hora_fin must be after hora_inicio")
		return self


class AppointmentCreate(AppointmentBase):
	pass


class AppointmentUpdate(BaseModel):
	cliente_id: Optional[int] = None
	servicio_id: Optional[int] = None
	fecha: Optional[date] = None
	hora_inicio: Optional[time] = None
	hora_fin: Optional[time] = None
	estado: Optional[AppointmentStatus] = None

	@model_validator(mode="after")
	def validate_times(self) -> "AppointmentUpdate":
		if self.hora_inicio is not None and self.hora_fin is not None:
			if self.hora_fin <= self.hora_inicio:
				raise ValueError("hora_fin must be after hora_inicio")
		return self


class AppointmentResponse(AppointmentBase):
	cita_id: int
	fecha_creacion: datetime

	class Config:
		from_attributes = True

