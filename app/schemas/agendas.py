import enum
from datetime import time
from typing import Optional

from pydantic import BaseModel, model_validator


class DayOfWeek(str, enum.Enum):
	LUNES = "LUNES"
	MARTES = "MARTES"
	MIERCOLES = "MIERCOLES"
	JUEVES = "JUEVES"
	VIERNES = "VIERNES"
	SABADO = "SABADO"
	DOMINGO = "DOMINGO"


class AgendaBase(BaseModel):
	establecimiento_id: int
	dia_semana: DayOfWeek
	hora_inicio: time
	hora_fin: time

	@model_validator(mode="after")
	def validate_times(self) -> "AgendaBase":
		if self.hora_fin <= self.hora_inicio:
			raise ValueError("hora_fin must be after hora_inicio")
		return self


class AgendaCreate(AgendaBase):
	pass


class AgendaUpdate(BaseModel):
	establecimiento_id: Optional[int] = None
	dia_semana: Optional[DayOfWeek] = None
	hora_inicio: Optional[time] = None
	hora_fin: Optional[time] = None

	@model_validator(mode="after")
	def validate_times(self) -> "AgendaUpdate":
		if self.hora_inicio is not None and self.hora_fin is not None:
			if self.hora_fin <= self.hora_inicio:
				raise ValueError("hora_fin must be after hora_inicio")
		return self


class AgendaResponse(AgendaBase):
	agenda_id: int

	class Config:
		from_attributes = True

