import enum

from datetime import time

from pydantic import BaseModel


class DayOfWeek(str, enum.Enum):
	LUNES = "LUNES"
	MARTES = "MARTES"
	MIERCOLES = "MIERCOLES"
	JUEVES = "JUEVES"
	VIERNES = "VIERNES"
	SABADO = "SABADO"
	DOMINGO = "DOMINGO"


class AgendaBase(BaseModel):
	trabajador_id: int
	dia_semana: DayOfWeek
	hora_inicio: time
	hora_fin: time


class AgendaCreate(AgendaBase):
	pass


class AgendaResponse(AgendaBase):
	agenda_id: int

	class Config:
		from_attributes = True

