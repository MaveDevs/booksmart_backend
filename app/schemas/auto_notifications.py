"""
Pydantic schemas for Automatic Notifications
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.auto_notifications import (
    AutoNotificationType,
    NotificationChannel,
    AutoNotificationStatus,
)


class AutoNotificationBase(BaseModel):
    usuario_id: int
    tipo: AutoNotificationType
    canal: NotificationChannel = NotificationChannel.IN_APP
    titulo: str = Field(..., max_length=200)
    mensaje: str
    fecha_programada: datetime
    url_accion: Optional[str] = Field(None, max_length=500)
    metadata: Optional[str] = Field(None, max_length=1000)


class AutoNotificationCreateWithRelations(AutoNotificationBase):
    cita_id: Optional[int] = None
    establecimiento_id: Optional[int] = None
    mensaje_id: Optional[int] = None
    pago_id: Optional[int] = None


class AutoNotificationCreate(AutoNotificationCreateWithRelations):
    pass


class AutoNotificationUpdate(BaseModel):
    usuario_id: Optional[int] = None
    tipo: Optional[AutoNotificationType] = None
    canal: Optional[NotificationChannel] = None
    titulo: Optional[str] = Field(None, max_length=200)
    mensaje: Optional[str] = None
    fecha_programada: Optional[datetime] = None
    url_accion: Optional[str] = Field(None, max_length=500)
    estado: Optional[AutoNotificationStatus] = None
    metadata: Optional[str] = Field(None, max_length=1000)


class AutoNotificationResponse(AutoNotificationBase):
    notif_auto_id: int
    cita_id: Optional[int] = None
    establecimiento_id: Optional[int] = None
    mensaje_id: Optional[int] = None
    pago_id: Optional[int] = None
    fecha_enviada: Optional[datetime] = None
    estado: AutoNotificationStatus
    intentos: int = 0
    ultimo_error: Optional[str] = None
    fecha_creacion: datetime

    class Config:
        from_attributes = True
