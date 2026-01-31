import enum
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


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
	monto: Decimal = Field(..., ge=0)
	metodo_pago: PaymentMethod
	estado: PaymentStatus = PaymentStatus.PENDIENTE


class PaymentCreate(PaymentBase):
	pass


class PaymentUpdate(BaseModel):
	suscripcion_id: Optional[int] = None
	monto: Optional[Decimal] = Field(None, ge=0)
	metodo_pago: Optional[PaymentMethod] = None
	estado: Optional[PaymentStatus] = None


class PaymentResponse(PaymentBase):
	pago_id: int
	fecha_pago: datetime

	class Config:
		from_attributes = True

