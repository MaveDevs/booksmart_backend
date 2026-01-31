import enum

from sqlalchemy import Column, Date, Enum, ForeignKey, Integer, Text, TIMESTAMP, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class AppointmentStatus(str, enum.Enum):
	PENDIENTE = "PENDIENTE"
	CONFIRMADA = "CONFIRMADA"
	CANCELADA = "CANCELADA"
	COMPLETADA = "COMPLETADA"


class Appointment(Base):
	__tablename__ = "cita"

	cita_id = Column(Integer, primary_key=True, autoincrement=True)
	cliente_id = Column(Integer, ForeignKey("usuario.usuario_id", ondelete="CASCADE"), nullable=False)
	servicio_id = Column(Integer, ForeignKey("servicio.servicio_id", ondelete="CASCADE"), nullable=False)
	fecha = Column(Date, nullable=False)
	hora_inicio = Column(Time, nullable=False)
	hora_fin = Column(Time, nullable=False)
	estado = Column(Enum(AppointmentStatus, native_enum=False), default=AppointmentStatus.PENDIENTE)
	fecha_creacion = Column(TIMESTAMP, server_default=func.now())

	client = relationship("User", foreign_keys=[cliente_id], back_populates="appointments")
	service = relationship("Service", back_populates="appointments")
	messages = relationship("Message", back_populates="appointment")

