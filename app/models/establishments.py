from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, TIMESTAMP
from sqlalchemy.dialects.mysql import DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

class Establishment(Base):
    __tablename__ = "Establecimiento"
    establecimiento_id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("Usuario.usuario_id", ondelete="CASCADE"))
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    direccion = Column(String(255))
    latitud = Column(DECIMAL(9, 6))
    longitud = Column(DECIMAL(9, 6))
    telefono = Column(String(20))
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())

    owner = relationship("User", back_populates="establishments")
    services = relationship("Service", back_populates="establishment")
    workers = relationship("Worker", back_populates="establishment")
    profile = relationship("Profile", back_populates="establishment", uselist=False)
    subscriptions = relationship("Subscription", back_populates="establishment")