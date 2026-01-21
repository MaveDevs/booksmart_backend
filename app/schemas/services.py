import enum

from datetime import date, datetime, time
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

class ServiceBase(BaseModel):
    establecimiento_id: int
    nombre: str
    descripcion: Optional[str] = None
    duracion: int
    precio: Decimal
    activo: bool = True

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    establecimiento_id: Optional[int] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    duracion: Optional[int] = None
    precio: Optional[Decimal] = None
    activo: Optional[bool] = None

class ServiceResponse(ServiceBase):
    servicio_id: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True


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


class MessageBase(BaseModel):
    cita_id: int
    emisor_id: int
    contenido: str


class MessageCreate(MessageBase):
    pass


class MessageResponse(MessageBase):
    mensaje_id: int
    fecha_envio: datetime

    class Config:
        from_attributes = True