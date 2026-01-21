import enum

from sqlalchemy import Column, Enum, ForeignKey, Integer, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


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


class Report(Base):
	__tablename__ = "Reporte"

	reporte_id = Column(Integer, primary_key=True, autoincrement=True)
	usuario_id = Column(Integer, ForeignKey("Usuario.usuario_id", ondelete="SET NULL"))
	tipo = Column(Enum(ReportType), nullable=False)
	entidad_id = Column(Integer, nullable=False)
	descripcion = Column(Text, nullable=False)
	estado = Column(Enum(ReportStatus), default=ReportStatus.PENDIENTE)
	fecha_creacion = Column(TIMESTAMP, server_default=func.now())
	fecha_resolucion = Column(TIMESTAMP, nullable=True)

	user = relationship("User", back_populates="reports")

