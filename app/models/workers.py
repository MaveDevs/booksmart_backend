from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text, TIMESTAMP, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class Worker(Base):
    __tablename__ = "Trabajador"

    trabajador_id = Column(Integer, primary_key=True, autoincrement=True)
    establecimiento_id = Column(Integer, ForeignKey("Establecimiento.establecimiento_id", ondelete="CASCADE"), nullable=False)
    nombre = Column(String(50), nullable=False)
    apellido = Column(String(50), nullable=False)
    email = Column(String(100))
    telefono = Column(String(20))
    foto_perfil = Column(String(255))
    especialidad = Column(String(100))
    descripcion = Column(Text)
    activo = Column(Boolean, default=True)
    fecha_contratacion = Column(Date)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())

    establishment = relationship("Establishment", back_populates="workers")

    worker_services = relationship("WorkerService", back_populates="worker")
    services = relationship("Service", secondary="TrabajadorServicio", back_populates="workers")

    agendas = relationship("Agenda", back_populates="worker")
    blocks = relationship("ScheduleBlock", back_populates="worker")

    appointments = relationship("Appointment", back_populates="worker")
    reviews = relationship("Review", back_populates="worker")


class WorkerService(Base):
    __tablename__ = "TrabajadorServicio"
    __table_args__ = (
        UniqueConstraint("trabajador_id", "servicio_id", name="unique_trabajador_servicio"),
    )

    trabajador_servicio_id = Column(Integer, primary_key=True, autoincrement=True)
    trabajador_id = Column(Integer, ForeignKey("Trabajador.trabajador_id", ondelete="CASCADE"), nullable=False)
    servicio_id = Column(Integer, ForeignKey("Servicio.servicio_id", ondelete="CASCADE"), nullable=False)

    worker = relationship("Worker", back_populates="worker_services")


class ScheduleBlock(Base):
    __tablename__ = "BloqueoAgenda"

    bloqueo_id = Column(Integer, primary_key=True, autoincrement=True)
    trabajador_id = Column(Integer, ForeignKey("Trabajador.trabajador_id", ondelete="CASCADE"), nullable=False)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime, nullable=False)
    motivo = Column(String(255))

    worker = relationship("Worker", back_populates="blocks")
