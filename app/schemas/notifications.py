import enum

from datetime import datetime

from pydantic import BaseModel


class NotificationType(str, enum.Enum):
	INFO = "INFO"
	ALERTA = "ALERTA"
	RECORDATORIO = "RECORDATORIO"


class NotificationBase(BaseModel):
	usuario_id: int
	mensaje: str
	tipo: NotificationType
	leido: bool = False


class NotificationCreate(NotificationBase):
	pass


class NotificationResponse(NotificationBase):
	notificacion_id: int
	fecha_envio: datetime

	class Config:
		from_attributes = True

