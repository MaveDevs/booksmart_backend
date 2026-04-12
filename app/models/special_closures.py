from datetime import date, datetime

from sqlalchemy import Column, Date, ForeignKey, Integer, String, TIMESTAMP, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class SpecialClosure(Base):
    __tablename__ = "special_closure"
    __table_args__ = (
        UniqueConstraint("establecimiento_id", "fecha", name="unique_establecimiento_fecha_cierre"),
    )

    cierre_id = Column(Integer, primary_key=True, autoincrement=True)
    establecimiento_id = Column(
        Integer,
        ForeignKey("establecimiento.establecimiento_id", ondelete="CASCADE"),
        nullable=False,
    )
    fecha = Column(Date, nullable=False)
    motivo = Column(String(255), nullable=True)
    creado_en = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)

    establishment = relationship("Establishment", back_populates="special_closures")