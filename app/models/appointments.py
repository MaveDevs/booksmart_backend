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
	__tablename__ = "Cita"

	cita_id = Column(Integer, primary_key=True, autoincrement=True)
	cliente_id = Column(Integer, ForeignKey("Usuario.usuario_id", ondelete="CASCADE"))
	trabajador_id = Column(Integer, ForeignKey("Trabajador.trabajador_id", ondelete="CASCADE"), nullable=False)
	servicio_id = Column(Integer, ForeignKey("Servicio.servicio_id", ondelete="CASCADE"))
	fecha = Column(Date, nullable=False)
	hora_inicio = Column(Time, nullable=False)
	hora_fin = Column(Time, nullable=False)
	estado = Column(Enum(AppointmentStatus), default=AppointmentStatus.PENDIENTE)
	notas_cliente = Column(Text)
	fecha_creacion = Column(TIMESTAMP, server_default=func.now())
	fecha_modificacion = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

	client = relationship("User", foreign_keys=[cliente_id], back_populates="appointments")
	worker = relationship("Worker", back_populates="appointments")
	service = relationship("Service", back_populates="appointments")
	messages = relationship("Message", back_populates="appointment")
	reviews = relationship("Review", back_populates="appointment")

