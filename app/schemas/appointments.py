import enum

from datetime import date, datetime, time
from typing import Optional

from pydantic import BaseModel


class AppointmentStatus(str, enum.Enum):
	PENDIENTE = "PENDIENTE"
	CONFIRMADA = "CONFIRMADA"
	CANCELADA = "CANCELADA"
	COMPLETADA = "COMPLETADA"


class AppointmentBase(BaseModel):
	cliente_id: Optional[int] = None
	trabajador_id: int
	servicio_id: Optional[int] = None
	fecha: date
	hora_inicio: time
	hora_fin: time
	estado: AppointmentStatus = AppointmentStatus.PENDIENTE
	notas_cliente: Optional[str] = None


class AppointmentCreate(AppointmentBase):
	pass


class AppointmentUpdate(BaseModel):
	trabajador_id: Optional[int] = None
	servicio_id: Optional[int] = None
	fecha: Optional[date] = None
	hora_inicio: Optional[time] = None
	hora_fin: Optional[time] = None
	estado: Optional[AppointmentStatus] = None
	notas_cliente: Optional[str] = None


class AppointmentResponse(AppointmentBase):
	cita_id: int
	fecha_creacion: datetime
	fecha_modificacion: datetime

	class Config:
		from_attributes = True

