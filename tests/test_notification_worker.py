import asyncio
from types import SimpleNamespace

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
    assert notification_worker._map_notification_type(AutoNotificationType.PAYMENT_FAILED) == NotificationType.ALERTA
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
