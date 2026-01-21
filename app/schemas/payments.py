import enum

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


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

