"""
Plan Features Model - Define qué características están habilitadas por plan
"""
import enum

from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class FeatureKey(str, enum.Enum):
    """Claves de features disponibles por plan"""
    # Automatizaciones
    AUTO_REMINDERS = "AUTO_REMINDERS"  # Recordatorios automáticos de citas
    AUTO_CONFIRMACION = "AUTO_CONFIRMACION"  # Confirmación automática de citas
    AUTO_RECOVERY = "AUTO_RECOVERY"  # Recuperación de citas canceladas
    AUTO_RESEÑA_PROMPT = "AUTO_RESEÑA_PROMPT"  # Solicitud automática de reseña
    
    # Impulsar/Destacar negocio
    DESTACADO_LISTING = "DESTACADO_LISTING"  # Boost en listados
    CAMPAÑAS_VISIBILIDAD = "CAMPAÑAS_VISIBILIDAD"  # Campañas de marketing
    
    # Analíticas
    ANALYTICS_OCUPACION = "ANALYTICS_OCUPACION"  # Analíticas de tiempos muertos
    ANALYTICS_CLIENTES = "ANALYTICS_CLIENTES"  # Segmentación de clientes
    SUGERIR_PROMOS = "SUGERIR_PROMOS"  # Sugerencias automáticas de promociones
    
    # Notificaciones avanzadas
    NOTIF_SMS = "NOTIF_SMS"  # Notificaciones por SMS (future)
    NOTIF_EMAIL = "NOTIF_EMAIL"  # Notificaciones por email (future)
    
    # Reportes avanzados
    REPORTES_AVANZADOS = "REPORTES_AVANZADOS"  # Reportes detallados


class PlanFeature(Base):
    """Matriz de features habilitados por plan"""
    __tablename__ = "plan_feature"

    plan_feature_id = Column(Integer, primary_key=True, autoincrement=True)
    plan_id = Column(Integer, ForeignKey("plan.plan_id", ondelete="CASCADE"), nullable=False)
    feature_key = Column(Enum(FeatureKey, native_enum=False), nullable=False)
    enabled = Column(Boolean, default=True)

    plan = relationship("Plan", back_populates="features")

    def __repr__(self):
        return f"<PlanFeature plan_id={self.plan_id} feature={self.feature_key} enabled={self.enabled}>"
