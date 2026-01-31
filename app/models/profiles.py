from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Profile(Base):
	__tablename__ = "perfil"

	perfil_id = Column(Integer, primary_key=True, autoincrement=True)
	establecimiento_id = Column(
		Integer,
		ForeignKey("establecimiento.establecimiento_id", ondelete="CASCADE"),
		unique=True,
	)
	descripcion_publica = Column(Text)
	imagen_logo = Column(String(255))
	imagen_portada = Column(String(255))

	establishment = relationship("Establishment", back_populates="profile")

