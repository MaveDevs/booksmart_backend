from sqlalchemy import Column, ForeignKey, Integer, TIMESTAMP
from sqlalchemy.sql import func
from app.db.base_class import Base

class WorkerService(Base):
    """
    Association table between Workers and Services (Many-to-Many).
    Defines which professional is qualified/assigned to perform which service.
    """
    __tablename__ = "trabajador_servicio"

    trabajador_id = Column(
        Integer, 
        ForeignKey("trabajador.trabajador_id", ondelete="CASCADE"), 
        primary_key=True
    )
    servicio_id = Column(
        Integer, 
        ForeignKey("servicio.servicio_id", ondelete="CASCADE"), 
        primary_key=True
    )
    fecha_asignacion = Column(TIMESTAMP, server_default=func.now())
