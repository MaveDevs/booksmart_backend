import enum

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ReportType(str, enum.Enum):
	USUARIO = "USUARIO"
	ESTABLECIMIENTO = "ESTABLECIMIENTO"
	SERVICIO = "SERVICIO"
	CITA = "CITA"
	TRABAJADOR = "TRABAJADOR"


class ReportStatus(str, enum.Enum):
	PENDIENTE = "PENDIENTE"
	EN_REVISION = "EN_REVISION"
	RESUELTO = "RESUELTO"
	RECHAZADO = "RECHAZADO"


class ReportBase(BaseModel):
	usuario_id: Optional[int] = None
	tipo: ReportType
	entidad_id: int
	descripcion: str
	estado: ReportStatus = ReportStatus.PENDIENTE


class ReportCreate(ReportBase):
	pass


class ReportResponse(ReportBase):
	reporte_id: int
	fecha_creacion: datetime
	fecha_resolucion: Optional[datetime] = None

	class Config:
		from_attributes = True

