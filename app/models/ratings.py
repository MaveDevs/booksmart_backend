from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, Text, TIMESTAMP, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class Review(Base):
	__tablename__ = "resena"
	__table_args__ = (
		CheckConstraint("calificacion >= 1 AND calificacion <= 5", name="check_calificacion_range"),
		UniqueConstraint("usuario_id", "establecimiento_id", name="unique_usuario_establecimiento_review"),
	)

	resena_id = Column(Integer, primary_key=True, autoincrement=True)
	establecimiento_id = Column(
		Integer,
		ForeignKey("establecimiento.establecimiento_id", ondelete="CASCADE"),
		nullable=False,
	)
	usuario_id = Column(Integer, ForeignKey("usuario.usuario_id", ondelete="CASCADE"), nullable=False)
	calificacion = Column(Integer, nullable=False)
	comentario = Column(Text)
	fecha = Column(TIMESTAMP, server_default=func.now())

	establishment = relationship("Establishment", back_populates="reviews")
	user = relationship("User", back_populates="reviews")

