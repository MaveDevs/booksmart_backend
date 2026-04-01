from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

class User(Base):
    __tablename__ = "usuario"
    usuario_id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    apellido = Column(String(50), nullable=False)
    correo = Column(String(100), unique=True, nullable=False)
    contrasena_hash = Column(String(255), nullable=False)
    rol_id = Column(Integer, ForeignKey("rol.rol_id", ondelete="SET NULL"))
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())

    role = relationship("Role", back_populates="users")
    establishments = relationship("Establishment", back_populates="owner")
    appointments = relationship("Appointment", foreign_keys="Appointment.cliente_id", back_populates="client")
    reviews = relationship("Review", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    sent_messages = relationship("Message", foreign_keys="Message.emisor_id", back_populates="sender")
    push_subscriptions = relationship("PushSubscription", back_populates="user")
    worker_profile = relationship("Worker", back_populates="user", uselist=False)
