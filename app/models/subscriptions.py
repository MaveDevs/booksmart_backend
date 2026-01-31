import enum

from sqlalchemy import Boolean, Column, Date, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class SubscriptionStatus(str, enum.Enum):
	ACTIVA = "ACTIVA"
	CANCELADA = "CANCELADA"
	EXPIRADA = "EXPIRADA"


class Subscription(Base):
	__tablename__ = "suscripcion"

	suscripcion_id = Column(Integer, primary_key=True, autoincrement=True)
	establecimiento_id = Column(Integer, ForeignKey("establecimiento.establecimiento_id", ondelete="CASCADE"))
	plan_id = Column(Integer, ForeignKey("plan.plan_id", ondelete="RESTRICT"))
	fecha_inicio = Column(Date, nullable=False)
	fecha_fin = Column(Date, nullable=True)
	estado = Column(Enum(SubscriptionStatus, native_enum=False), default=SubscriptionStatus.ACTIVA)

	establishment = relationship("Establishment", back_populates="subscriptions")
	plan = relationship("Plan", back_populates="subscriptions")
	payments = relationship("Payment", back_populates="subscription")

