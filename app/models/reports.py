from sqlalchemy import Column, ForeignKey, Integer, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class Report(Base):
	__tablename__ = "reporte"

	reporte_id = Column(Integer, primary_key=True, autoincrement=True)
	establecimiento_id = Column(
		Integer,
		ForeignKey("establecimiento.establecimiento_id", ondelete="CASCADE"),
		nullable=False,
	)
	descripcion = Column(Text, nullable=False)
	fecha_generacion = Column(TIMESTAMP, server_default=func.now())

	establishment = relationship("Establishment", back_populates="reports")

