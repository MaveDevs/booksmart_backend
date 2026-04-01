import enum

from sqlalchemy import Column, Enum, ForeignKey, Integer, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class ReportStatus(str, enum.Enum):
	PENDIENTE = "PENDIENTE"
	EN_REVISION = "EN_REVISION"
	RESUELTO = "RESUELTO"
	RECHAZADO = "RECHAZADO"


class Report(Base):
	__tablename__ = "reporte"

	reporte_id = Column(Integer, primary_key=True, autoincrement=True)
	establecimiento_id = Column(
		Integer,
		ForeignKey("establecimiento.establecimiento_id", ondelete="CASCADE"),
		nullable=False,
	)
	descripcion = Column(Text, nullable=False)
	estado = Column(Enum(ReportStatus, name="reportstatus", native_enum=False), default=ReportStatus.PENDIENTE, nullable=False)
	fecha_generacion = Column(TIMESTAMP, server_default=func.now())

	establishment = relationship("Establishment", back_populates="reports")

