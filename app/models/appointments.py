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
	trabajador_id = Column(Integer, ForeignKey("trabajador.trabajador_id", ondelete="SET NULL"), nullable=True)
	fecha = Column(Date, nullable=False)
	hora_inicio = Column(Time, nullable=False)
	hora_fin = Column(Time, nullable=False)
	estado = Column(Enum(AppointmentStatus, native_enum=False), default=AppointmentStatus.PENDIENTE)
	fecha_creacion = Column(TIMESTAMP, server_default=func.now())

	client = relationship("User", foreign_keys=[cliente_id], back_populates="appointments")
	service = relationship("Service", back_populates="appointments")
	worker = relationship("Worker")
	messages = relationship("Message", back_populates="appointment")

	# Propiedades calculadas para facilitar la vida al esquema Pydantic
	@property
	def cliente_nombre(self):
		return self.client.nombre if self.client else None

	@property
	def cliente_apellido(self):
		return self.client.apellido if self.client else None

	@property
	def trabajador_nombre(self):
		return self.worker.nombre if self.worker else None

	@property
	def trabajador_apellido(self):
		return self.worker.apellido if self.worker else None
