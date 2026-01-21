from sqlalchemy import Column, ForeignKey, Integer, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class Message(Base):
	__tablename__ = "Mensaje"

	mensaje_id = Column(Integer, primary_key=True, autoincrement=True)
	cita_id = Column(Integer, ForeignKey("Cita.cita_id", ondelete="CASCADE"))
	emisor_id = Column(Integer, ForeignKey("Usuario.usuario_id", ondelete="CASCADE"))
	contenido = Column(Text, nullable=False)
	fecha_envio = Column(TIMESTAMP, server_default=func.now())

	appointment = relationship("Appointment", back_populates="messages")
	sender = relationship("User", foreign_keys=[emisor_id], back_populates="sent_messages")

