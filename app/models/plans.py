from sqlalchemy import Boolean, Column, Integer, String, Text
from sqlalchemy.dialects.mysql import DECIMAL
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Plan(Base):
	__tablename__ = "Plan"

	plan_id = Column(Integer, primary_key=True, autoincrement=True)
	nombre = Column(String(50), nullable=False, unique=True)
	descripcion = Column(Text)
	precio_mensual = Column(DECIMAL(10, 2), nullable=False)
	max_servicios = Column(Integer, default=10)
	max_trabajadores = Column(Integer, default=5)
	max_citas_mes = Column(Integer, default=100)
	activo = Column(Boolean, default=True)

	subscriptions = relationship("Subscription", back_populates="plan")

