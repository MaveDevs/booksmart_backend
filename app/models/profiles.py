from sqlalchemy import Column, ForeignKey, Integer, String, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class Profile(Base):
	__tablename__ = "Perfil"

	perfil_id = Column(Integer, primary_key=True, autoincrement=True)
	establecimiento_id = Column(
		Integer,
		ForeignKey("Establecimiento.establecimiento_id", ondelete="CASCADE"),
		unique=True,
	)
	descripcion_publica = Column(Text)
	imagen_logo = Column(String(255))
	imagen_portada = Column(String(255))
	fecha_actualizacion = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

	establishment = relationship("Establishment", back_populates="profile")

