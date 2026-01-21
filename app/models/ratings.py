from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, Text, TIMESTAMP, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class Review(Base):
	__tablename__ = "Resena"
	__table_args__ = (
		CheckConstraint("calificacion >= 1 AND calificacion <= 5", name="check_calificacion_range"),
		UniqueConstraint("cita_id", "usuario_id", name="unique_cita_usuario"),
	)

	resena_id = Column(Integer, primary_key=True, autoincrement=True)
	trabajador_id = Column(Integer, ForeignKey("Trabajador.trabajador_id", ondelete="CASCADE"), nullable=False)
	cita_id = Column(Integer, ForeignKey("Cita.cita_id", ondelete="SET NULL"))
	usuario_id = Column(Integer, ForeignKey("Usuario.usuario_id", ondelete="CASCADE"))
	calificacion = Column(Integer)
	comentario = Column(Text)
	fecha_creacion = Column(TIMESTAMP, server_default=func.now())

	worker = relationship("Worker", back_populates="reviews")
	appointment = relationship("Appointment", back_populates="reviews")
	user = relationship("User", back_populates="reviews")

