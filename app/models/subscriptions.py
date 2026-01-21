import enum

from sqlalchemy import Boolean, Column, Date, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class SubscriptionStatus(str, enum.Enum):
	ACTIVA = "ACTIVA"
	CANCELADA = "CANCELADA"
	EXPIRADA = "EXPIRADA"


class Subscription(Base):
	__tablename__ = "Suscripcion"

	suscripcion_id = Column(Integer, primary_key=True, autoincrement=True)
	establecimiento_id = Column(Integer, ForeignKey("Establecimiento.establecimiento_id", ondelete="CASCADE"))
	plan_id = Column(Integer, ForeignKey("Plan.plan_id", ondelete="RESTRICT"))
	fecha_inicio = Column(Date, nullable=False)
	fecha_fin = Column(Date, nullable=True)
	estado = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVA)
	auto_renovacion = Column(Boolean, default=True)

	establishment = relationship("Establishment", back_populates="subscriptions")
	plan = relationship("Plan", back_populates="subscriptions")
	payments = relationship("Payment", back_populates="subscription")

