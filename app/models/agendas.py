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
	__tablename__ = "agenda"
	__table_args__ = (
		UniqueConstraint("establecimiento_id", "dia_semana", name="unique_establecimiento_dia"),
	)

	agenda_id = Column(Integer, primary_key=True, autoincrement=True)
	establecimiento_id = Column(
		Integer,
		ForeignKey("establecimiento.establecimiento_id", ondelete="CASCADE"),
		nullable=False,
	)
	dia_semana = Column(Enum(DayOfWeek, native_enum=False), nullable=False)
	hora_inicio = Column(Time, nullable=False)
	hora_fin = Column(Time, nullable=False)

	establishment = relationship("Establishment", back_populates="agendas")

