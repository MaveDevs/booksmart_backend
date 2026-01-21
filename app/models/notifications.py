import enum

from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class NotificationType(str, enum.Enum):
	INFO = "INFO"
	ALERTA = "ALERTA"
	RECORDATORIO = "RECORDATORIO"


class Notification(Base):
	__tablename__ = "Notificacion"

	notificacion_id = Column(Integer, primary_key=True, autoincrement=True)
	usuario_id = Column(Integer, ForeignKey("Usuario.usuario_id", ondelete="CASCADE"))
	mensaje = Column(Text, nullable=False)
	tipo = Column(Enum(NotificationType), nullable=False)
	leido = Column(Boolean, default=False)
	fecha_envio = Column(TIMESTAMP, server_default=func.now())

	user = relationship("User", back_populates="notifications")

