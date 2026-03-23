"""
Automatic Notifications Model - Scheduled notifications triggered by business events

This model stores notifications that will be sent automatically based on:
- Appointment reminders (T-24h, T-2h before appointment)
- Appointment status changes (confirmation, completion)
- Message notifications
- Payment notifications
- Cancellation recovery flows
"""

import enum
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class AutoNotificationType(str, enum.Enum):
    """Types of automatic notifications"""
    APPOINTMENT_REMINDER = "APPOINTMENT_REMINDER"  # Recordatorio de cita
    APPOINTMENT_CONFIRMATION = "APPOINTMENT_CONFIRMATION"  # Confirmación de cita
    APPOINTMENT_COMPLETION = "APPOINTMENT_COMPLETION"  # Cita completada
    APPOINTMENT_CANCELLATION = "APPOINTMENT_CANCELLATION"  # Cancelación de cita
    MESSAGE_RECEIVED = "MESSAGE_RECEIVED"  # Nuevo mensaje
    PAYMENT_FAILED = "PAYMENT_FAILED"  # Pago fallido
    REVIEW_REQUEST = "REVIEW_REQUEST"  # Solicitud de reseña
    RECOVERY_OFFER = "RECOVERY_OFFER"  # Oferta de recuperación (cancelación)


class NotificationChannel(str, enum.Enum):
    """Delivery channels for notifications"""
    IN_APP = "IN_APP"  # Store in notificacion table
    PUSH = "PUSH"  # Web push
    EMAIL = "EMAIL"  # Email (future)
    SMS = "SMS"  # SMS (future)


class AutoNotificationStatus(str, enum.Enum):
    """Status of automatic notification"""
    PENDING = "PENDING"  # Waiting to be sent
    SENT = "SENT"  # Successfully sent
    FAILED = "FAILED"  # Failed to send
    CANCELLED = "CANCELLED"  # Manually cancelled


class AutoNotification(Base):
    """Automatic notifications scheduled for delivery"""
    __tablename__ = "notificacion_automatica"

    notif_auto_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Target user
    usuario_id = Column(Integer, ForeignKey("usuario.usuario_id", ondelete="CASCADE"), nullable=False)
    
    # Related entities (all optional to allow flexibility)
    cita_id = Column(Integer, ForeignKey("cita.cita_id", ondelete="CASCADE"), nullable=True)
    establecimiento_id = Column(Integer, ForeignKey("establecimiento.establecimiento_id", ondelete="CASCADE"), nullable=True)
    mensaje_id = Column(Integer, ForeignKey("mensaje.mensaje_id", ondelete="CASCADE"), nullable=True)
    pago_id = Column(Integer, ForeignKey("pago.pago_id", ondelete="SET NULL"), nullable=True)
    
    # Notification details
    tipo = Column(Enum(AutoNotificationType, native_enum=False), nullable=False)
    canal = Column(Enum(NotificationChannel, native_enum=False), default=NotificationChannel.IN_APP)
    titulo = Column(String(200), nullable=False)
    mensaje = Column(Text, nullable=False)
    url_accion = Column(String(500), nullable=True)  # Link to take action (e.g., confirm appointment)
    
    # Scheduling
    fecha_programada = Column(DateTime, nullable=False)  # When to send
    fecha_enviada = Column(DateTime, nullable=True)  # When actually sent
    estado = Column(Enum(AutoNotificationStatus, native_enum=False), default=AutoNotificationStatus.PENDING)
    intentos = Column(Integer, default=0)  # Number of send attempts
    ultimo_error = Column(Text, nullable=True)  # Last error message if FAILED
    
    # Metadata
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())
    metadata = Column(String(1000), nullable=True)  # JSON string with additional data

    # Relationships (optional, for convenience)
    user = relationship("User", foreign_keys=[usuario_id])
    appointment = relationship("Appointment", foreign_keys=[cita_id])
    establishment = relationship("Establishment", foreign_keys=[establecimiento_id])

    def __repr__(self):
        return f"<AutoNotification id={self.notif_auto_id} tipo={self.tipo} estado={self.estado}>"
