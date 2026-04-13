import asyncio
from datetime import date, time
from types import SimpleNamespace

from app.crud import crud_appointments, crud_messages
from app.schemas.notifications import NotificationType
import pytest


def _make_appointment():
    return SimpleNamespace(
        cita_id=101,
        cliente_id=42,
        servicio_id=7,
        fecha=date(2026, 4, 20),
        hora_inicio=time(14, 30),
        service=SimpleNamespace(
            nombre="Corte premium",
            establishment=SimpleNamespace(nombre="Barbería Central"),
        ),
        worker=SimpleNamespace(usuario_id=88),
    )


async def _noop_async(*_args, **_kwargs):
    return None


class _FakeDB:
    def query(self, *_args, **_kwargs):
        raise AssertionError("Unexpected database query in content test")


def test_confirmed_notification_includes_business_and_service(monkeypatch):
    from app.services.notification_orchestrator import orchestrator

    appointment = _make_appointment()
    captured_notifications = []

    monkeypatch.setattr(
        "app.services.notification_orchestrator.get_appointment",
        lambda _db, _id: appointment,
    )
    monkeypatch.setattr(
        "app.services.notification_orchestrator.crud_notifications.create_notification",
        lambda _db, notification: captured_notifications.append(notification) or SimpleNamespace(
            notificacion_id=1,
            usuario_id=notification.usuario_id,
            mensaje=notification.mensaje,
            tipo=notification.tipo,
            leida=notification.leida,
            fecha_envio=None,
        ),
    )
    monkeypatch.setattr("app.services.notification_orchestrator.notify_user", _noop_async)
    monkeypatch.setattr(
        "app.services.notification_orchestrator.create_auto_notification",
        lambda *_args, **_kwargs: None,
    )

    asyncio.run(orchestrator.on_appointment_confirmed(_FakeDB(), appointment.cita_id, 55))

    assert len(captured_notifications) == 1
    notification = captured_notifications[0]
    assert notification.tipo == NotificationType.ALERTA
    assert "Barbería Central" in notification.mensaje
    assert "Corte premium" in notification.mensaje
    assert "confirmada" in notification.mensaje


def test_cancelled_notification_includes_reason_and_context(monkeypatch):
    from app.services.notification_orchestrator import orchestrator

    appointment = _make_appointment()
    captured_notifications = []
    reason = "Cliente pidió reprogramar"

    monkeypatch.setattr(
        "app.services.notification_orchestrator.get_appointment",
        lambda _db, _id: appointment,
    )
    monkeypatch.setattr(
        "app.services.notification_orchestrator.crud_notifications.create_notification",
        lambda _db, notification: captured_notifications.append(notification) or SimpleNamespace(
            notificacion_id=2,
            usuario_id=notification.usuario_id,
            mensaje=notification.mensaje,
            tipo=notification.tipo,
            leida=notification.leida,
            fecha_envio=None,
        ),
    )
    monkeypatch.setattr("app.services.notification_orchestrator.notify_user", _noop_async)
    monkeypatch.setattr(
        "app.services.notification_orchestrator.create_auto_notification",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.notification_orchestrator.establishment_has_feature",
        lambda *_args, **_kwargs: False,
    )

    asyncio.run(
        orchestrator.on_appointment_cancelled(
            _FakeDB(), appointment.cita_id, 55, reason=reason
        )
    )

    assert len(captured_notifications) == 1
    notification = captured_notifications[0]
    assert notification.tipo == NotificationType.ALERTA
    assert "Barbería Central" in notification.mensaje
    assert "Corte premium" in notification.mensaje
    assert reason in notification.mensaje
    assert "cancelada" in notification.mensaje


def test_completed_notification_includes_context_and_review_request(monkeypatch):
    from app.services.notification_orchestrator import orchestrator

    appointment = _make_appointment()
    captured_notifications = []
    captured_auto_notifications = []

    monkeypatch.setattr(
        "app.services.notification_orchestrator.get_appointment",
        lambda _db, _id: appointment,
    )
    monkeypatch.setattr(
        "app.services.notification_orchestrator.establishment_has_feature",
        lambda *_args, **_kwargs: True,
    )
    monkeypatch.setattr(
        "app.services.notification_orchestrator.crud_notifications.create_notification",
        lambda _db, notification: captured_notifications.append(notification) or SimpleNamespace(
            notificacion_id=3,
            usuario_id=notification.usuario_id,
            mensaje=notification.mensaje,
            tipo=notification.tipo,
            leida=notification.leida,
            fecha_envio=None,
        ),
    )
    monkeypatch.setattr("app.services.notification_orchestrator.notify_user", _noop_async)
    monkeypatch.setattr(
        "app.services.notification_orchestrator.create_auto_notification",
        lambda _db, notification: captured_auto_notifications.append(notification),
    )

    asyncio.run(orchestrator.on_appointment_completed(_FakeDB(), appointment.cita_id, 55))

    assert len(captured_notifications) == 1
    notification = captured_notifications[0]
    assert notification.tipo == NotificationType.ALERTA
    assert "Barbería Central" in notification.mensaje
    assert "Corte premium" in notification.mensaje
    assert "completada" in notification.mensaje

    assert len(captured_auto_notifications) == 1
    assert "Barbería Central" in captured_auto_notifications[0].mensaje
    assert "Corte premium" in captured_auto_notifications[0].mensaje


def test_message_notification_includes_context_and_preview(monkeypatch):
    from app.services.notification_orchestrator import orchestrator

    appointment = _make_appointment()
    message = SimpleNamespace(
        appointment=appointment,
        emisor_id=42,
        contenido="Necesito cambiar la hora de mi cita",
    )
    captured_notifications = []

    monkeypatch.setattr(
        "app.services.notification_orchestrator.get_message",
        lambda _db, _id: message,
    )
    monkeypatch.setattr(
        "app.services.notification_orchestrator.crud_notifications.create_notification",
        lambda _db, notification: captured_notifications.append(notification) or SimpleNamespace(
            notificacion_id=4,
            usuario_id=notification.usuario_id,
            mensaje=notification.mensaje,
            tipo=notification.tipo,
            leida=notification.leida,
            fecha_envio=None,
        ),
    )
    monkeypatch.setattr("app.services.notification_orchestrator.notify_user", _noop_async)
    monkeypatch.setattr("app.services.notification_orchestrator.notify_new_message", _noop_async)
    monkeypatch.setattr(
        "app.services.notification_orchestrator.create_auto_notification",
        lambda *_args, **_kwargs: None,
    )

    asyncio.run(orchestrator.on_message_received(_FakeDB(), 900, 55))

    assert len(captured_notifications) == 1
    notification = captured_notifications[0]
    assert notification.tipo == NotificationType.INFO
    assert "Barbería Central" in notification.mensaje
    assert "Corte premium" in notification.mensaje
    assert "Nuevo mensaje sobre tu cita" in notification.mensaje
    assert "Necesito cambiar la hora" in notification.mensaje


@pytest.mark.parametrize(
    ("action", "reason", "expected_message"),
    [
        (
            "confirmed",
            None,
            "Tu cita en Barbería Central para el servicio Corte premium el 20/04/2026 a las 14:30 fue confirmada.",
        ),
        (
            "cancelled",
            "Cliente pidió reprogramar",
            "Tu cita en Barbería Central para el servicio Corte premium el 20/04/2026 a las 14:30 fue cancelada. Motivo: Cliente pidió reprogramar",
        ),
        (
            "completed",
            None,
            "Tu cita en Barbería Central para el servicio Corte premium el 20/04/2026 a las 14:30 fue marcada como completada.",
        ),
    ],
)
def test_appointment_update_notification_text_is_exact(monkeypatch, action, reason, expected_message):
    from app.services.notification_orchestrator import orchestrator

    appointment = _make_appointment()
    captured_notifications = []

    monkeypatch.setattr(
        "app.services.notification_orchestrator.get_appointment",
        lambda _db, _id: appointment,
    )
    monkeypatch.setattr(
        "app.services.notification_orchestrator.crud_notifications.create_notification",
        lambda _db, notification: captured_notifications.append(notification) or SimpleNamespace(
            notificacion_id=10,
            usuario_id=notification.usuario_id,
            mensaje=notification.mensaje,
            tipo=notification.tipo,
            leida=notification.leida,
            fecha_envio=None,
        ),
    )
    monkeypatch.setattr("app.services.notification_orchestrator.notify_user", _noop_async)
    monkeypatch.setattr(
        "app.services.notification_orchestrator.create_auto_notification",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.notification_orchestrator.establishment_has_feature",
        lambda *_args, **_kwargs: True,
    )

    db = _FakeDB()

    if action == "confirmed":
        asyncio.run(orchestrator.on_appointment_confirmed(db, appointment.cita_id, 55))
    elif action == "cancelled":
        asyncio.run(orchestrator.on_appointment_cancelled(db, appointment.cita_id, 55, reason=reason))
    else:
        asyncio.run(orchestrator.on_appointment_completed(db, appointment.cita_id, 55))

    assert len(captured_notifications) == 1
    assert captured_notifications[0].mensaje == expected_message
