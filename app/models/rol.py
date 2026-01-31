from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Role(Base):
	__tablename__ = "rol"

	rol_id = Column(Integer, primary_key=True, autoincrement=True)
	nombre = Column(String(50), nullable=False, unique=True)
	descripcion = Column(Text)

	users = relationship("User", back_populates="role")

