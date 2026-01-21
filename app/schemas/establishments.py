import enum

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

class EstablishmentBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    direccion: Optional[str] = None
    latitud: Optional[float] = Field(None, ge=-90, le=90)
    longitud: Optional[float] = Field(None, ge=-180, le=180)
    telefono: Optional[str] = None
    usuario_id: int
    activo: bool = True

class EstablishmentCreate(EstablishmentBase):
    pass

class EstablishmentUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    direccion: Optional[str] = None
    latitud: Optional[float] = Field(None, ge=-90, le=90)
    longitud: Optional[float] = Field(None, ge=-180, le=180)
    telefono: Optional[str] = None
    usuario_id: Optional[int] = None
    activo: Optional[bool] = None

class EstablishmentResponse(EstablishmentBase):
    establecimiento_id: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True


class ProfileBase(BaseModel):
    establecimiento_id: int
    descripcion_publica: Optional[str] = None
    imagen_logo: Optional[str] = None
    imagen_portada: Optional[str] = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(BaseModel):
    descripcion_publica: Optional[str] = None
    imagen_logo: Optional[str] = None
    imagen_portada: Optional[str] = None


class ProfileResponse(ProfileBase):
    perfil_id: int
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True


class ReviewBase(BaseModel):
    trabajador_id: int
    cita_id: Optional[int] = None
    usuario_id: int
    calificacion: Optional[int] = Field(None, ge=1, le=5)
    comentario: Optional[str] = None


class ReviewCreate(ReviewBase):
    pass


class ReviewResponse(ReviewBase):
    resena_id: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True


class PlanBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio_mensual: Decimal
    max_servicios: int = 10
    max_trabajadores: int = 5
    max_citas_mes: int = 100
    activo: bool = True


class PlanCreate(PlanBase):
    pass


class PlanResponse(PlanBase):
    plan_id: int

    class Config:
        from_attributes = True


class SubscriptionStatus(str, enum.Enum):
    ACTIVA = "ACTIVA"
    CANCELADA = "CANCELADA"
    EXPIRADA = "EXPIRADA"


class SubscriptionBase(BaseModel):
    establecimiento_id: int
    plan_id: int
    fecha_inicio: date
    fecha_fin: Optional[date] = None
    estado: SubscriptionStatus = SubscriptionStatus.ACTIVA
    auto_renovacion: bool = True


class SubscriptionCreate(SubscriptionBase):
    pass


class SubscriptionResponse(SubscriptionBase):
    suscripcion_id: int

    class Config:
        from_attributes = True


class PaymentMethod(str, enum.Enum):
    TARJETA_CREDITO = "TARJETA_CREDITO"
    PAYPAL = "PAYPAL"
    TRANSFERENCIA_BANCARIA = "TRANSFERENCIA_BANCARIA"


class PaymentStatus(str, enum.Enum):
    COMPLETADO = "COMPLETADO"
    PENDIENTE = "PENDIENTE"
    FALLIDO = "FALLIDO"
    REEMBOLSADO = "REEMBOLSADO"


class PaymentBase(BaseModel):
    suscripcion_id: int
    monto: Decimal
    metodo_pago: PaymentMethod
    transaccion_id: Optional[str] = None
    estado: PaymentStatus = PaymentStatus.PENDIENTE


class PaymentCreate(PaymentBase):
    pass


class PaymentResponse(PaymentBase):
    pago_id: int
    fecha_pago: datetime

    class Config:
        from_attributes = True