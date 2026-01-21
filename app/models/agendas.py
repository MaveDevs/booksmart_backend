import enum

from sqlalchemy import Column, Enum, ForeignKey, Integer, Time, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class DayOfWeek(str, enum.Enum):
	LUNES = "LUNES"
	MARTES = "MARTES"
	MIERCOLES = "MIERCOLES"
	JUEVES = "JUEVES"
	VIERNES = "VIERNES"
	SABADO = "SABADO"
	DOMINGO = "DOMINGO"


class Agenda(Base):
	__tablename__ = "Agenda"
	__table_args__ = (
		UniqueConstraint("trabajador_id", "dia_semana", name="unique_trabajador_dia"),
	)

	agenda_id = Column(Integer, primary_key=True, autoincrement=True)
	trabajador_id = Column(Integer, ForeignKey("Trabajador.trabajador_id", ondelete="CASCADE"), nullable=False)
	dia_semana = Column(Enum(DayOfWeek), nullable=False)
	hora_inicio = Column(Time, nullable=False)
	hora_fin = Column(Time, nullable=False)

	worker = relationship("Worker", back_populates="agendas")

