import enum
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class NotificationType(str, enum.Enum):
	INFO = "INFO"
	ALERTA = "ALERTA"
	RECORDATORIO = "RECORDATORIO"


class NotificationBase(BaseModel):
	usuario_id: int
	mensaje: str = Field(..., min_length=1)
	tipo: NotificationType
	leida: bool = False


class NotificationCreate(NotificationBase):
	pass


class NotificationUpdate(BaseModel):
	usuario_id: Optional[int] = None
	mensaje: Optional[str] = Field(None, min_length=1)
	tipo: Optional[NotificationType] = None
	leida: Optional[bool] = None


class NotificationResponse(NotificationBase):
	notificacion_id: int
	fecha_envio: datetime

	class Config:
		from_attributes = True

