import asyncio
import json
import logging
from typing import Dict

from app.crud import crud_auto_notifications
from app.crud.crud_push_subscriptions import (
    delete_subscription,
    get_subscriptions_by_user,
)
from app.db.session import SessionLocal
from app.models import Notification
from app.models.auto_notifications import (
    AutoNotification,
    AutoNotificationType,
    NotificationChannel,
)
from app.models.notifications import Notification
from app.models.notifications import NotificationType
from app.services.push_sender import send_push

logger = logging.getLogger(__name__)


def _map_notification_type(auto_type: AutoNotificationType) -> NotificationType:
    if auto_type in (
        AutoNotificationType.APPOINTMENT_REMINDER,
        AutoNotificationType.REVIEW_REQUEST,
    ):
        return NotificationType.RECORDATORIO

    if auto_type in (
        AutoNotificationType.APPOINTMENT_CONFIRMATION,
        AutoNotificationType.APPOINTMENT_COMPLETION,
        AutoNotificationType.APPOINTMENT_CANCELLATION,
        AutoNotificationType.RECOVERY_OFFER,
        AutoNotificationType.PAYMENT_FAILED,
    ):
        return NotificationType.ALERTA

    return NotificationType.INFO


def _should_skip_endpoint_entry(notification: AutoNotification) -> bool:
    metadata_value = getattr(notification, "metadata_json", None)
    if not metadata_value:
        return False

    try:
        metadata = json.loads(metadata_value)
    except (TypeError, json.JSONDecodeError):
        return False

    return bool(metadata.get("mirror_to_notifications"))


def _create_endpoint_notification(db, notification: AutoNotification) -> None:
    if _should_skip_endpoint_entry(notification):
        return

    endpoint_notification = Notification(
        usuario_id=notification.usuario_id,
        mensaje=notification.mensaje,
        tipo=_map_notification_type(notification.tipo),
        leida=False,
    )
    db.add(endpoint_notification)
    db.commit()


def _deliver_push_notification(db, notification: AutoNotification) -> bool:
    subscriptions = get_subscriptions_by_user(db, notification.usuario_id)
    if not subscriptions:
        crud_auto_notifications.mark_failed(
            db,
            notification.notif_auto_id,
            "No push subscriptions for target user",
        )
        return False

    delivered = False
    errors = []

    for subscription in subscriptions:
        try:
            is_valid = send_push(
                endpoint=subscription.endpoint,
                p256dh=subscription.p256dh,
                auth=subscription.auth,
                title=notification.titulo,
                body=notification.mensaje,
                url=notification.url_accion or "/app/home",
            )
            if is_valid:
                delivered = True
            else:
                delete_subscription(db, notification.usuario_id, subscription.endpoint)
        except Exception as exc:
            errors.append(str(exc))

    if delivered:
        crud_auto_notifications.mark_sent(db, notification.notif_auto_id)
        return True

    error_msg = "; ".join(errors[:3]) or "Push delivery failed for all subscriptions"
    crud_auto_notifications.mark_failed(db, notification.notif_auto_id, error_msg)
    return False


def _deliver_notification(db, notification: AutoNotification) -> bool:
    _create_endpoint_notification(db, notification)

    channel = notification.canal

    if channel == NotificationChannel.IN_APP:
        crud_auto_notifications.mark_sent(db, notification.notif_auto_id)
        return True

    if channel == NotificationChannel.PUSH:
        return _deliver_push_notification(db, notification)

    crud_auto_notifications.mark_failed(
        db,
        notification.notif_auto_id,
        f"Channel {channel.value} not implemented yet",
    )
    return False


async def process_pending_notifications_once(limit: int = 200) -> Dict[str, int]:
    db = SessionLocal()
    stats = {
        "processed": 0,
        "sent": 0,
        "failed": 0,
    }

    try:
        pending = crud_auto_notifications.get_pending_notifications(db, limit=limit)

        for notification in pending:
            stats["processed"] += 1
            try:
                success = _deliver_notification(db, notification)
                if success:
                    stats["sent"] += 1
                else:
                    stats["failed"] += 1
            except Exception as exc:
                stats["failed"] += 1
                logger.exception(
                    "Failed processing auto notification %s",
                    notification.notif_auto_id,
                )
                crud_auto_notifications.mark_failed(
                    db,
                    notification.notif_auto_id,
                    str(exc)[:1000],
                )

    finally:
        db.close()

    return stats


async def run_notification_worker(
    poll_seconds: int = 60,
    batch_size: int = 200,
    stop_event: asyncio.Event | None = None,
) -> None:
    logger.info(
        "Notification worker started (poll_seconds=%s, batch_size=%s)",
        poll_seconds,
        batch_size,
    )

    while True:
        if stop_event and stop_event.is_set():
            logger.info("Notification worker stop signal received")
            return

        try:
            stats = await process_pending_notifications_once(limit=batch_size)
            if stats["processed"] > 0:
                logger.info("Notification worker cycle: %s", stats)
        except Exception:
            logger.exception("Unexpected error in notification worker cycle")

        if stop_event:
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=poll_seconds)
            except asyncio.TimeoutError:
                pass
        else:
            await asyncio.sleep(poll_seconds)
