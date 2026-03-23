"""
Occupancy Analytics Model - Track business occupancy and idle times

Stores aggregated metrics about appointment occupancy to help owners:
- Identify dead times (low occupancy hours)
- Suggest promotional campaigns
- Understand peak hours
- Calculate occupancy rates
"""

import enum
from datetime import date, time

from sqlalchemy import Column, Date, Enum, Float, ForeignKey, Integer, String, Text, Time, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class DayOfWeek(str, enum.Enum):
    """Days of week for occupancy tracking"""
    LUNES = "LUNES"
    MARTES = "MARTES"
    MIERCOLES = "MIERCOLES"
    JUEVES = "JUEVES"
    VIERNES = "VIERNES"
    SABADO = "SABADO"
    DOMINGO = "DOMINGO"


class OccupancyAnalytics(Base):
    """
    Daily occupancy metrics per time slot.
    
    Example: 
        - 2025-01-20, LUNES, 09:00-10:00, 80% ocupación, 0 no-shows
        - 2025-01-20, LUNES, 15:00-16:00, 20% ocupación (IDLE TIME)
    """
    __tablename__ = "analytics_ocupacion"

    analytics_id = Column(Integer, primary_key=True, autoincrement=True)
    establecimiento_id = Column(Integer, ForeignKey("establecimiento.establecimiento_id", ondelete="CASCADE"), nullable=False)
    
    # Time period
    fecha = Column(Date, nullable=False)  # Date
    dia_semana = Column(Enum(DayOfWeek, native_enum=False), nullable=False)  # Day name
    hora_inicio = Column(Time, nullable=False)  # Start time (e.g., 09:00)
    hora_fin = Column(Time, nullable=False)  # End time (e.g., 10:00)
    
    # Occupancy metrics
    capacidad_total = Column(Integer, default=0)  # Total appointments possible in this slot
    citas_confirmadas = Column(Integer, default=0)  # Confirmed appointments
    citas_completadas = Column(Integer, default=0)  # Completed appointments
    citas_canceladas = Column(Integer, default=0)  # Cancelled appointments
    citas_pendientes = Column(Integer, default=0)  # Pending appointments
    
    # Calculated rates (percentages 0-100)
    tasa_ocupacion = Column(Float, default=0.0)  # Occupancy rate (booked / total)
    tasa_no_show = Column(Float, default=0.0)  # No-show rate (confirmed but not completed / confirmed)
    tasa_cancelacion = Column(Float, default=0.0)  # Cancellation rate
    
    # Ingresos (if available from service pricing)
    ingresos_estimados = Column(Float, default=0.0)  # Estimated revenue for this slot
    
    # Metadata
    calculado_en = Column(TIMESTAMP, server_default=func.now())  # When metrics were calculated
    
    # Relationships
    establishment = relationship("Establishment", foreign_keys=[establecimiento_id])

    def __repr__(self):
        return f"<OccupancyAnalytics est={self.establecimiento_id} {self.fecha} {self.hora_inicio}>"


class SuggestionPromocion(Base):
    """
    Suggested promotions based on occupancy analysis.
    
    Example:
        - "Tu horario 15:00-17:00 está bajo (20% ocupación). Ofrece 20% descuento"
    """
    __tablename__ = "sugerencia_promocion"

    sugerencia_id = Column(Integer, primary_key=True, autoincrement=True)
    establecimiento_id = Column(Integer, ForeignKey("establecimiento.establecimiento_id", ondelete="CASCADE"), nullable=False)
    
    # Suggestion details
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=False)
    
    # Context
    hora_inicio = Column(Time, nullable=True)  # Idle time start
    hora_fin = Column(Time, nullable=True)  # Idle time end
    tasa_ocupacion = Column(Float, nullable=True)  # Current occupancy rate
    descuento_sugerido = Column(Float, default=20.0)  # Suggested discount %
    
    # Status
    visto = Column(Boolean, default=False)
    implementado = Column(Boolean, default=False)
    
    # Metadata
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())
    
    establishment = relationship("Establishment", foreign_keys=[establecimiento_id])

    def __repr__(self):
        return f"<SuggestionPromocion est={self.establecimiento_id} {self.titulo}>"
