from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, TIMESTAMP
from sqlalchemy.dialects.mysql import DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

class Service(Base):
    __tablename__ = "Servicio"
    servicio_id = Column(Integer, primary_key=True, autoincrement=True)
    establecimiento_id = Column(Integer, ForeignKey("Establecimiento.establecimiento_id", ondelete="CASCADE"))
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    duracion = Column(Integer, nullable=False)
    precio = Column(DECIMAL(10, 2), nullable=False)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())

    establishment = relationship("Establishment", back_populates="services")
    workers = relationship("Worker", secondary="TrabajadorServicio", back_populates="services")
    appointments = relationship("Appointment", back_populates="service")