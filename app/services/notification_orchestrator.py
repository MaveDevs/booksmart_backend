"""
Notification Orchestrator - Centralized logic for triggering automatic notifications

This module listens to business events (appointment created, message sent, etc.)
and automatically creates AutoNotification records based on the establishment's
feature entitlements.

Usage example:
    from app.services.notification_orchestrator import orchestrator
    
    # When appointment is created:
    await orchestrator.on_appointment_created(db, appointment_id, establishment_id)
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Optional, cast

from sqlalchemy.orm import Session

from app.crud.crud_auto_notifications import create_auto_notification
from app.crud import crud_notifications
from app.crud.crud_appointments import get_appointment
from app.crud.crud_messages import get_message
from app.core.feature_gating import establishment_has_feature
from app.models.auto_notifications import (
    AutoNotificationType,
    NotificationChannel,
)
from app.models.establishments import Establishment
from app.models.services import Service
from app.models.plan_features import FeatureKey
from app.schemas.auto_notifications import AutoNotificationCreate
from app.schemas.notifications import NotificationCreate, NotificationType
from app.services.realtime import notify_new_message, notify_user


class NotificationOrchestrator:
    """
    Orchestrates automatic notification creation based on business events.
    All methods are safe to call even if features are not enabled (they will no-op).
    """

    def _get_appointment_context(
        self, db: Session, appointment, establishment_id: int
    ) -> tuple[str, str]:
        """Resolve business and service names for appointment notifications."""
        service_name = getattr(appointment, "servicio_nombre", None)
        business_name = None

        service = getattr(appointment, "service", None)
        if service:
            service_name = service_name or getattr(service, "nombre", None)
            establishment = getattr(service, "establishment", None)
            if establishment:
                business_name = getattr(establishment, "nombre", None)

        if not service_name and getattr(appointment, "servicio_id", None) is not None:
            service = db.query(Service).filter(Service.servicio_id == appointment.servicio_id).first()
            if service:
                service_name = getattr(service, "nombre", None)
                establishment = getattr(service, "establishment", None)
                if establishment:
                    business_name = business_name or getattr(establishment, "nombre", None)

        if not business_name and establishment_id is not None:
            establishment = (
                db.query(Establishment)
                .filter(Establishment.establecimiento_id == establishment_id)
                .first()
            )
            if establishment:
                business_name = getattr(establishment, "nombre", None)

        return business_name or "tu negocio", service_name or "tu servicio"

    def _format_appointment_label(self, appointment) -> str:
        fecha = getattr(appointment, "fecha", None)
        hora_inicio = getattr(appointment, "hora_inicio", None)

        if fecha is None or hora_inicio is None:
            return "en la fecha programada"

        return f"el {fecha.strftime('%d/%m/%Y')} a las {hora_inicio.strftime('%H:%M')}"

    def _build_appointment_message(self, db: Session, appointment, establishment_id: int, action: str, reason: Optional[str] = None) -> str:
        business_name, service_name = self._get_appointment_context(db, appointment, establishment_id)
        appointment_label = self._format_appointment_label(appointment)

        base_message = (
            f"Tu cita en {business_name} para el servicio {service_name} {appointment_label}"
        )

        if action == "created":
            return f"{base_message} fue registrada correctamente."
        if action == "confirmed":
            return f"{base_message} fue confirmada."
        if action == "cancelled":
            if reason:
                return f"{base_message} fue cancelada. Motivo: {reason}"
            return f"{base_message} fue cancelada."
        if action == "completed":
            return f"{base_message} fue marcada como completada."

        return base_message

    async def on_appointment_created(
        self, db: Session, appointment_id: int, establishment_id: int
    ) -> None:
        """
        Called when a new appointment is created.
        Schedules reminder notifications if AUTO_REMINDERS feature is enabled.
        """
        has_reminders = establishment_has_feature(db, establishment_id, FeatureKey.AUTO_REMINDERS)
        if not has_reminders:
            return

        appointment = get_appointment(db, appointment_id)
        if not appointment:
            return
        appointment = cast(Any, appointment)

        # Schedule reminders: T-24h and T-2h before appointment
        appointment_datetime = datetime.combine(appointment.fecha, appointment.hora_inicio)

        # 24-hour reminder
        reminder_24h = appointment_datetime - timedelta(hours=24)
        if reminder_24h > datetime.utcnow():
            notif_24h = AutoNotificationCreate(
                usuario_id=appointment.cliente_id,
                cita_id=appointment_id,
                establecimiento_id=establishment_id,
                tipo=AutoNotificationType.APPOINTMENT_REMINDER,
                canal=NotificationChannel.PUSH,
                titulo="Recordatorio: Tu cita es mañana",
                mensaje=f"Tu cita está programada para mañana a las {appointment.hora_inicio.strftime('%H:%M')}",
                fecha_programada=reminder_24h,
                url_accion="/app/appointments",
                metadata=None,
            )
            create_auto_notification(db, notif_24h)

        # 2-hour reminder
        reminder_2h = appointment_datetime - timedelta(hours=2)
        if reminder_2h > datetime.utcnow():
            notif_2h = AutoNotificationCreate(
                usuario_id=appointment.cliente_id,
                cita_id=appointment_id,
                establecimiento_id=establishment_id,
                tipo=AutoNotificationType.APPOINTMENT_REMINDER,
                canal=NotificationChannel.PUSH,
                titulo="Recordatorio: Tu cita es en 2 horas",
                mensaje=f"Tu cita comienza a las {appointment.hora_inicio.strftime('%H:%M')}",
                fecha_programada=reminder_2h,
                url_accion="/app/appointments",
                metadata=None,
            )
            create_auto_notification(db, notif_2h)

    async def on_appointment_confirmed(
        self, db: Session, appointment_id: int, establishment_id: int
    ) -> None:
        """
        Called when an appointment is confirmed by owner.
        Creates confirmation notification.
        """
        appointment = get_appointment(db, appointment_id)
        if not appointment:
            return
        appointment = cast(Any, appointment)

        message = self._build_appointment_message(db, appointment, establishment_id, "confirmed")

        in_app_notification = crud_notifications.create_notification(
            db,
            NotificationCreate(
                usuario_id=appointment.cliente_id,
                mensaje=message,
                tipo=NotificationType.ALERTA,
                leida=False,
            ),
        )
        await notify_user(appointment.cliente_id, in_app_notification)

        notif = AutoNotificationCreate(
            usuario_id=appointment.cliente_id,
            cita_id=appointment_id,
            establecimiento_id=establishment_id,
            tipo=AutoNotificationType.APPOINTMENT_CONFIRMATION,
            canal=NotificationChannel.PUSH,
            titulo="Tu cita ha sido confirmada",
            mensaje=message,
            fecha_programada=datetime.utcnow(),
            url_accion="/app/appointments",
                metadata=json.dumps({"mirror_to_notifications": True, "source": "appointment_update"}),
        )
        create_auto_notification(db, notif)

    async def on_appointment_cancelled(
        self, db: Session, appointment_id: int, establishment_id: int, reason: Optional[str] = None
    ) -> None:
        """
        Called when an appointment is cancelled.
        Notifies client and optionally suggests recovery offer if feature is enabled.
        """
        appointment = get_appointment(db, appointment_id)
        if not appointment:
            return
        appointment = cast(Any, appointment)

        message = self._build_appointment_message(
            db,
            appointment,
            establishment_id,
            "cancelled",
            reason=reason,
        )

        in_app_notification = crud_notifications.create_notification(
            db,
            NotificationCreate(
                usuario_id=appointment.cliente_id,
                mensaje=message,
                tipo=NotificationType.ALERTA,
                leida=False,
            ),
        )
        await notify_user(appointment.cliente_id, in_app_notification)

        notif = AutoNotificationCreate(
            usuario_id=appointment.cliente_id,
            cita_id=appointment_id,
            establecimiento_id=establishment_id,
            tipo=AutoNotificationType.APPOINTMENT_CANCELLATION,
            canal=NotificationChannel.PUSH,
            titulo="Tu cita ha sido cancelada",
            mensaje=message,
            fecha_programada=datetime.utcnow(),
            url_accion=None,
            metadata=json.dumps({"mirror_to_notifications": True, "source": "appointment_update"}),
        )
        create_auto_notification(db, notif)

        # Recovery offer if feature enabled
        has_recovery = establishment_has_feature(db, establishment_id, FeatureKey.AUTO_RECOVERY)
        if has_recovery:
            recovery_notif = AutoNotificationCreate(
                usuario_id=appointment.cliente_id,
                establecimiento_id=establishment_id,
                tipo=AutoNotificationType.RECOVERY_OFFER,
                canal=NotificationChannel.PUSH,
                titulo="¡Te extrañamos! Obtén un descuento",
                mensaje="Reserva tu próxima cita y obtén 20% de descuento como disculpa.",
                fecha_programada=datetime.utcnow() + timedelta(minutes=5),
                url_accion="/app/appointments",
                metadata=None,
            )
            create_auto_notification(db, recovery_notif)

    async def on_appointment_completed(
        self, db: Session, appointment_id: int, establishment_id: int
    ) -> None:
        """
        Called when an appointment is marked as completed.
        Triggers review request if feature is enabled.
        """
        has_review_prompt = establishment_has_feature(
            db, establishment_id, FeatureKey.AUTO_RESEÑA_PROMPT
        )
        if not has_review_prompt:
            return

        appointment = get_appointment(db, appointment_id)
        if not appointment:
            return
        appointment = cast(Any, appointment)

        message = self._build_appointment_message(db, appointment, establishment_id, "completed")

        in_app_notification = crud_notifications.create_notification(
            db,
            NotificationCreate(
                usuario_id=appointment.cliente_id,
                mensaje=message,
                tipo=NotificationType.ALERTA,
                leida=False,
            ),
        )
        await notify_user(appointment.cliente_id, in_app_notification)

        # Schedule review request 1 hour after appointment
        review_request = AutoNotificationCreate(
            usuario_id=appointment.cliente_id,
            cita_id=appointment_id,
            establecimiento_id=establishment_id,
            tipo=AutoNotificationType.REVIEW_REQUEST,
            canal=NotificationChannel.IN_APP,
            titulo="¿Cómo fue tu experiencia?",
            mensaje=message,
            fecha_programada=datetime.utcnow() + timedelta(hours=1),
            url_accion="/app/ratings",
            metadata=None,
        )
        create_auto_notification(db, review_request)

    async def on_message_received(
        self, db: Session, message_id: int, establishment_id: int
    ) -> None:
        """
        Called when a new message is received in a conversation.
        Creates notification for the recipient.
        """
        message = get_message(db, message_id)
        if not message or not message.appointment:
            return

        message = cast(Any, message)
        appointment = cast(Any, message.appointment)

        # Determine recipient (client <-> worker/owner)
        if message.emisor_id == appointment.cliente_id:
            recipient_id = None
            if appointment.worker and appointment.worker.usuario_id:
                recipient_id = appointment.worker.usuario_id
            else:
                establishment = (
                    db.query(Establishment)
                    .filter(Establishment.establecimiento_id == establishment_id)
                    .first()
                )
                if establishment:
                    recipient_id = establishment.usuario_id
        else:
            recipient_id = appointment.cliente_id

        recipient_id = cast(Optional[int], recipient_id)
        if recipient_id is None or recipient_id == message.emisor_id:
            return

        business_name, service_name = self._get_appointment_context(db, appointment, establishment_id)
        content = (message.contenido or "").strip()
        preview = content[:100]
        if len(content) > 100:
            preview = f"{preview}..."

        notification_message = (
            f"Nuevo mensaje sobre tu cita en {business_name} para el servicio {service_name}: {preview}"
        )

        in_app_notification = crud_notifications.create_notification(
            db,
            NotificationCreate(
                usuario_id=recipient_id,
                mensaje=notification_message,
                tipo=NotificationType.INFO,
                leida=False,
            ),
        )
        await notify_user(recipient_id, in_app_notification)

        notif = AutoNotificationCreate(
            usuario_id=recipient_id,
            mensaje_id=message_id,
            cita_id=appointment.cita_id,
            establecimiento_id=establishment_id,
            tipo=AutoNotificationType.MESSAGE_RECEIVED,
            canal=NotificationChannel.PUSH,
            titulo="Nuevo mensaje",
            mensaje=notification_message,
            fecha_programada=datetime.utcnow(),
            url_accion=f"/app/appointments/{appointment.cita_id}",
            metadata=json.dumps({"mirror_to_notifications": True, "source": "message_update"}),
        )
        create_auto_notification(db, notif)

        await notify_new_message(recipient_id, message)

    def _run_sync(self, coro) -> None:
        """Run coroutine from sync contexts, including AnyIO worker threads."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(coro)
            return

        loop.create_task(coro)

    def on_appointment_created_sync(
        self, db: Session, appointment_id: int, establishment_id: int
    ) -> None:
        """
        Synchronous version of on_appointment_created.
        Use this from sync CRUD contexts.
        """
        try:
            self._run_sync(self.on_appointment_created(db, appointment_id, establishment_id))
        except Exception as e:
            # Log and continue - notifications are non-critical
            logging.error(f"Notification orchestration failed: {e}")

    def on_appointment_confirmed_sync(
        self, db: Session, appointment_id: int, establishment_id: int
    ) -> None:
        """Synchronous version of on_appointment_confirmed"""
        try:
            self._run_sync(self.on_appointment_confirmed(db, appointment_id, establishment_id))
        except Exception as e:
            logging.error(f"Notification orchestration failed: {e}")

    def on_appointment_cancelled_sync(
        self,
        db: Session,
        appointment_id: int,
        establishment_id: int,
        reason: Optional[str] = None,
    ) -> None:
        """Synchronous version of on_appointment_cancelled"""
        try:
            self._run_sync(
                self.on_appointment_cancelled(db, appointment_id, establishment_id, reason)
            )
        except Exception as e:
            logging.error(f"Notification orchestration failed: {e}")

    def on_appointment_completed_sync(
        self, db: Session, appointment_id: int, establishment_id: int
    ) -> None:
        """Synchronous version of on_appointment_completed"""
        try:
            self._run_sync(self.on_appointment_completed(db, appointment_id, establishment_id))
        except Exception as e:
            logging.error(f"Notification orchestration failed: {e}")

    def on_message_received_sync(
        self, db: Session, message_id: int, establishment_id: int
    ) -> None:
        """Synchronous version of on_message_received"""
        try:
            self._run_sync(self.on_message_received(db, message_id, establishment_id))
        except Exception as e:
            logging.error(f"Notification orchestration failed: {e}")


# Global orchestrator instance
orchestrator = NotificationOrchestrator()
