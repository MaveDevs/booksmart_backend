"""
Service layer for sending real-time events over WebSocket.

Import and call these helpers from CRUD or endpoint code to push
live updates to connected clients.

Usage:
    from app.services.realtime import notify_user, notify_new_appointment

    # After creating a notification in the DB:
    await notify_user(user_id=42, notification=db_notification)

    # From a sync context (e.g. inside a CRUD function):
    import asyncio
    asyncio.get_event_loop().run_until_complete(notify_user(42, db_notification))
    # — OR use the sync wrapper —
    send_realtime_sync(user_id=42, event_type="notification", data={...})
"""

import asyncio
import logging
from typing import Any, Dict, Optional

from app.core.websocket_manager import manager

logger = logging.getLogger(__name__)


# ── Async helpers (call from async endpoints) ───────────────────────────────

async def notify_user(user_id: int, notification) -> None:
    """Push a notification object to a user over WebSocket."""
    await manager.send_personal(user_id, {
        "type": "notification",
        "data": {
            "notificacion_id": notification.notificacion_id,
            "mensaje": notification.mensaje,
            "tipo": notification.tipo.value if hasattr(notification.tipo, "value") else str(notification.tipo),
            "leida": notification.leida,
            "fecha_envio": str(notification.fecha_envio),
        },
    })


async def notify_new_message(recipient_id: int, message) -> None:
    """Push a new chat message to the recipient."""
    await manager.send_personal(recipient_id, {
        "type": "message",
        "data": {
            "mensaje_id": message.mensaje_id,
            "cita_id": message.cita_id,
            "emisor_id": message.emisor_id,
            "contenido": message.contenido,
            "fecha_envio": str(message.fecha_envio),
        },
    })


async def notify_appointment_update(user_id: int, appointment, event: str = "updated") -> None:
    """Push an appointment event (created, updated, cancelled) to a user."""
    await manager.send_personal(user_id, {
        "type": "appointment",
        "event": event,
        "data": {
            "cita_id": appointment.cita_id,
            "estado": appointment.estado if isinstance(appointment.estado, str) else appointment.estado.value,
        },
    })


async def send_realtime(user_id: int, event_type: str, data: Dict[str, Any]) -> None:
    """Generic: push any event to a user."""
    await manager.send_personal(user_id, {"type": event_type, "data": data})


async def broadcast_event(event_type: str, data: Dict[str, Any]) -> None:
    """Push an event to ALL connected users."""
    await manager.broadcast({"type": event_type, "data": data})


# ── Sync wrapper (safe to call from synchronous CRUD code) ──────────────────

def send_realtime_sync(user_id: int, event_type: str, data: Dict[str, Any]) -> None:
    """
    Fire-and-forget sync wrapper. Works from sync endpoint/CRUD code.
    If no event loop is running it silently skips (e.g. during tests).
    """
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(send_realtime(user_id, event_type, data))
    except RuntimeError:
        # No running event loop — skip silently (CLI, tests, etc.)
        logger.debug("No event loop; skipping realtime push to user %s", user_id)
