import asyncio
import os
from types import SimpleNamespace

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_worker.sqlite3")

from app.models.auto_notifications import AutoNotificationType, NotificationChannel
from app.models.notifications import NotificationType
from app.tasks import notification_worker


class _FakeDB:
    def __init__(self):
        self.added = []
        self.commits = 0
        self.closed = False

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        self.commits += 1

    def close(self):
        self.closed = True


def test_map_notification_type():
    assert notification_worker._map_notification_type(AutoNotificationType.APPOINTMENT_REMINDER) == NotificationType.RECORDATORIO
    assert notification_worker._map_notification_type(AutoNotificationType.APPOINTMENT_CONFIRMATION) == NotificationType.ALERTA
    assert notification_worker._map_notification_type(AutoNotificationType.APPOINTMENT_COMPLETION) == NotificationType.ALERTA
    assert notification_worker._map_notification_type(AutoNotificationType.PAYMENT_FAILED) == NotificationType.ALERTA
    assert notification_worker._map_notification_type(AutoNotificationType.RECOVERY_OFFER) == NotificationType.ALERTA
    assert notification_worker._map_notification_type(AutoNotificationType.MESSAGE_RECEIVED) == NotificationType.INFO


def test_process_pending_notifications_once_counts(monkeypatch):
    db = _FakeDB()

    notif_ok = SimpleNamespace(
        notif_auto_id=1,
        usuario_id=10,
        tipo=AutoNotificationType.MESSAGE_RECEIVED,
        canal=NotificationChannel.IN_APP,
        titulo="t",
        mensaje="m",
        url_accion=None,
    )
    notif_fail = SimpleNamespace(
        notif_auto_id=2,
        usuario_id=20,
        tipo=AutoNotificationType.MESSAGE_RECEIVED,
        canal=NotificationChannel.EMAIL,
        titulo="t2",
        mensaje="m2",
        url_accion=None,
    )

    sent = []
    failed = []

    monkeypatch.setattr(notification_worker, "SessionLocal", lambda: db)
    monkeypatch.setattr(
        notification_worker.crud_auto_notifications,
        "get_pending_notifications",
        lambda _db, limit=200: [notif_ok, notif_fail],
    )
    monkeypatch.setattr(
        notification_worker.crud_auto_notifications,
        "mark_sent",
        lambda _db, notif_auto_id: sent.append(notif_auto_id),
    )
    monkeypatch.setattr(
        notification_worker.crud_auto_notifications,
        "mark_failed",
        lambda _db, notif_auto_id, msg=None: failed.append((notif_auto_id, msg)),
    )

    stats = asyncio.run(notification_worker.process_pending_notifications_once())

    assert stats == {"processed": 2, "sent": 1, "failed": 1}
    assert sent == [1]
    assert failed and failed[0][0] == 2
    assert db.closed is True


def test_process_pending_notifications_once_posts_push_notification_to_endpoint(monkeypatch):
    db = _FakeDB()

    notif_push = SimpleNamespace(
        notif_auto_id=3,
        usuario_id=30,
        tipo=AutoNotificationType.APPOINTMENT_REMINDER,
        canal=NotificationChannel.PUSH,
        titulo="t3",
        mensaje="m3",
        url_accion="/app/appointments",
        metadata_json=None,
    )

    sent = []
    monkeypatch.setattr(notification_worker, "SessionLocal", lambda: db)
    monkeypatch.setattr(
        notification_worker.crud_auto_notifications,
        "get_pending_notifications",
        lambda _db, limit=200: [notif_push],
    )
    monkeypatch.setattr(
        notification_worker.crud_auto_notifications,
        "mark_sent",
        lambda _db, notif_auto_id: sent.append(notif_auto_id),
    )
    monkeypatch.setattr(notification_worker, "get_subscriptions_by_user", lambda *_args, **_kwargs: [SimpleNamespace(endpoint="ep", p256dh="p", auth="a")])
    monkeypatch.setattr(notification_worker, "send_push", lambda **_kwargs: True)

    stats = asyncio.run(notification_worker.process_pending_notifications_once())

    assert stats == {"processed": 1, "sent": 1, "failed": 0}
    assert len(db.added) == 1
    assert db.added[0].mensaje == "m3"
    assert db.added[0].tipo == NotificationType.RECORDATORIO
    assert sent == [3]
    assert db.closed is True


def test_process_pending_notifications_once_skips_mirrored_endpoint_duplicate(monkeypatch):
    db = _FakeDB()

    notif_push = SimpleNamespace(
        notif_auto_id=4,
        usuario_id=40,
        tipo=AutoNotificationType.APPOINTMENT_CONFIRMATION,
        canal=NotificationChannel.PUSH,
        titulo="t4",
        mensaje="m4",
        url_accion="/app/appointments",
        metadata_json='{"mirror_to_notifications": true}',
    )

    sent = []
    monkeypatch.setattr(notification_worker, "SessionLocal", lambda: db)
    monkeypatch.setattr(
        notification_worker.crud_auto_notifications,
        "get_pending_notifications",
        lambda _db, limit=200: [notif_push],
    )
    monkeypatch.setattr(
        notification_worker.crud_auto_notifications,
        "mark_sent",
        lambda _db, notif_auto_id: sent.append(notif_auto_id),
    )
    monkeypatch.setattr(notification_worker, "get_subscriptions_by_user", lambda *_args, **_kwargs: [SimpleNamespace(endpoint="ep", p256dh="p", auth="a")])
    monkeypatch.setattr(notification_worker, "send_push", lambda **_kwargs: True)

    stats = asyncio.run(notification_worker.process_pending_notifications_once())

    assert stats == {"processed": 1, "sent": 1, "failed": 0}
    assert db.added == []
    assert sent == [4]
    assert db.closed is True
