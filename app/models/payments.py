import enum

from sqlalchemy import Column, Enum, ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy.dialects.mysql import DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class PaymentMethod(str, enum.Enum):
	TARJETA_CREDITO = "TARJETA_CREDITO"
	PAYPAL = "PAYPAL"
	TRANSFERENCIA_BANCARIA = "TRANSFERENCIA_BANCARIA"


class PaymentStatus(str, enum.Enum):
	COMPLETADO = "COMPLETADO"
	PENDIENTE = "PENDIENTE"
	FALLIDO = "FALLIDO"
	REEMBOLSADO = "REEMBOLSADO"


class Payment(Base):
	__tablename__ = "pago"

	pago_id = Column(Integer, primary_key=True, autoincrement=True)
	suscripcion_id = Column(Integer, ForeignKey("suscripcion.suscripcion_id", ondelete="CASCADE"))
	monto = Column(DECIMAL(10, 2), nullable=False)
	metodo_pago = Column(Enum(PaymentMethod, native_enum=False), nullable=False)
	fecha_pago = Column(TIMESTAMP, server_default=func.now())
	estado = Column(Enum(PaymentStatus, native_enum=False), default=PaymentStatus.PENDIENTE)

	subscription = relationship("Subscription", back_populates="payments")

