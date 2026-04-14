from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class Worker(Base):
	__tablename__ = "trabajador"
	
	trabajador_id = Column(Integer, primary_key=True, autoincrement=True)
	establecimiento_id = Column(Integer, ForeignKey("establecimiento.establecimiento_id", ondelete="CASCADE"), nullable=False)
	usuario_id = Column(Integer, ForeignKey("usuario.usuario_id", ondelete="SET NULL"), nullable=True)
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
	user = relationship("User", back_populates="worker_profiles")
	
	# Relationship many-to-many with services
	services = relationship("Service", secondary="trabajador_servicio", back_populates="workers")
