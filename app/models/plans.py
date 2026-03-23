from sqlalchemy import Boolean, Column, Integer, String, Text
from sqlalchemy.dialects.mysql import DECIMAL
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Plan(Base):
	__tablename__ = "plan"

	plan_id = Column(Integer, primary_key=True, autoincrement=True)
	nombre = Column(String(50), nullable=False, unique=True)
	descripcion = Column(Text)
	precio = Column(DECIMAL(10, 2), nullable=False)
	activo = Column(Boolean, default=True)

	subscriptions = relationship("Subscription", back_populates="plan")
	features = relationship("PlanFeature", back_populates="plan", cascade="all, delete-orphan")

