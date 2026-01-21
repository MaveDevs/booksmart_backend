import enum

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class RoleBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class RoleResponse(RoleBase):
    rol_id: int

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    nombre: str
    apellido: str
    correo: EmailStr
    rol_id: Optional[int] = None
    activo: bool = True

class UserCreate(UserBase):
    contrasena: str

class UserUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    correo: Optional[EmailStr] = None
    contrasena: Optional[str] = None
    rol_id: Optional[int] = None
    activo: Optional[bool] = None

class UserResponse(UserBase):
    usuario_id: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True


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


class ReportType(str, enum.Enum):
    USUARIO = "USUARIO"
    ESTABLECIMIENTO = "ESTABLECIMIENTO"
    SERVICIO = "SERVICIO"
    CITA = "CITA"
    TRABAJADOR = "TRABAJADOR"


class ReportStatus(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    EN_REVISION = "EN_REVISION"
    RESUELTO = "RESUELTO"
    RECHAZADO = "RECHAZADO"


class ReportBase(BaseModel):
    usuario_id: Optional[int] = None
    tipo: ReportType
    entidad_id: int
    descripcion: str
    estado: ReportStatus = ReportStatus.PENDIENTE


class ReportCreate(ReportBase):
    pass


class ReportResponse(ReportBase):
    reporte_id: int
    fecha_creacion: datetime
    fecha_resolucion: Optional[datetime] = None

    class Config:
        from_attributes = True