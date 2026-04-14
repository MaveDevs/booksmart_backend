from datetime import date, time
from types import SimpleNamespace

from app.crud import crud_appointments, crud_messages
from app.schemas.appointments import AppointmentCreate, AppointmentStatus, AppointmentUpdate
from app.schemas.messages import MessageCreate


class _FakeQuery:
    def __init__(self, value):
        self._value = value

    def filter(self, *_args, **_kwargs):
        return self

    def join(self, *_args, **_kwargs):
        return self

    def first(self):
        # If it's a list, return first item, else just return value
        if isinstance(self._value, list):
            return self._value[0] if self._value else None
        return self._value

    def all(self):
        # Ensure it returns a list
        if self._value is None:
            return []
        if isinstance(self._value, list):
            return self._value
        return [self._value]


class _FakeDB:
    def __init__(self, query_map):
        self.query_map = query_map
        self.added = []
        self.commits = 0

    def query(self, model):
        value = self.query_map.get(model)
        return _FakeQuery(value)

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        self.commits += 1

    def refresh(self, obj):
        if not hasattr(obj, "cita_id") or obj.cita_id is None:
            obj.cita_id = 123
        if not hasattr(obj, "mensaje_id") or obj.mensaje_id is None:
            obj.mensaje_id = 456


def test_create_appointment_triggers_orchestrator(monkeypatch):
    from app.models import Service, User, Worker
    from app.services.notification_orchestrator import orchestrator

    service = SimpleNamespace(servicio_id=7, establecimiento_id=55, duracion=30)
    client = SimpleNamespace(usuario_id=42)
    worker = SimpleNamespace(trabajador_id=1, establecimiento_id=55, services=[service], activo=True)
    
    db = _FakeDB({
        User: client, 
        Service: service,
        Worker: [worker]
    })

    calls = []
    monkeypatch.setattr(
        orchestrator,
        "on_appointment_created_sync",
        lambda _db, appointment_id, establishment_id: calls.append((appointment_id, establishment_id)),
    )

    appointment = AppointmentCreate(
        cliente_id=42,
        servicio_id=7,
        fecha=date(2026, 3, 22),
        hora_inicio=time(10, 0),
        hora_fin=time(11, 0),
    )

    created = crud_appointments.create_appointment(db, appointment)

    assert created.cita_id == 123
    assert calls == [(123, 55)]


def test_update_appointment_status_change_triggers_confirmed(monkeypatch):
    from datetime import date, time
    from app.models import Service, User
    from app.services.notification_orchestrator import orchestrator
    from app.models.notifications import Notification

    existing = SimpleNamespace(
        cita_id=999,
        cliente_id=42,
        servicio_id=5,
        estado=AppointmentStatus.PENDIENTE,
        fecha=date(2026, 4, 20),
        hora_inicio=time(14, 30),
    )
    service = SimpleNamespace(servicio_id=5, establecimiento_id=66, nombre="Corte premium", establishment=SimpleNamespace(nombre="Barbería Central"))
    client = SimpleNamespace(usuario_id=42)
    db = _FakeDB({Service: service, User: client})

    monkeypatch.setattr(crud_appointments, "get_appointment", lambda _db, _id: existing)

    confirmed_calls = []
    monkeypatch.setattr(
        orchestrator,
        "on_appointment_confirmed_sync",
        lambda _db, appointment_id, establishment_id, create_endpoint_notification=True: confirmed_calls.append((appointment_id, establishment_id, create_endpoint_notification)),
    )

    updated = crud_appointments.update_appointment(
        db,
        appointment_id=999,
        appointment=AppointmentUpdate(estado=AppointmentStatus.CONFIRMADA),
    )

    assert updated.estado == AppointmentStatus.CONFIRMADA
    assert confirmed_calls == [(999, 66, False)]
    assert len(db.added) == 1
    assert isinstance(db.added[0], Notification)
    assert db.added[0].usuario_id == 42
    assert "Barbería Central" in db.added[0].mensaje
    assert "Corte premium" in db.added[0].mensaje


def test_update_appointment_status_change_triggers_rejected_notification(monkeypatch):
    from datetime import date, time
    from app.models import Service, User
    from app.services.notification_orchestrator import orchestrator
    from app.models.notifications import Notification

    existing = SimpleNamespace(
        cita_id=1001,
        cliente_id=50,
        servicio_id=6,
        estado=AppointmentStatus.PENDIENTE,
        fecha=date(2026, 4, 21),
        hora_inicio=time(9, 0),
    )
    service = SimpleNamespace(servicio_id=6, establecimiento_id=77, nombre="Corte barba", establishment=SimpleNamespace(nombre="La Barbería"))
    client = SimpleNamespace(usuario_id=50)
    db = _FakeDB({Service: service, User: client})

    monkeypatch.setattr(crud_appointments, "get_appointment", lambda _db, _id: existing)

    rejected_calls = []
    monkeypatch.setattr(
        orchestrator,
        "on_appointment_cancelled_sync",
        lambda _db, appointment_id, establishment_id, reason=None, create_endpoint_notification=True: rejected_calls.append((appointment_id, establishment_id, reason, create_endpoint_notification)),
    )

    updated = crud_appointments.update_appointment(
        db,
        appointment_id=1001,
        appointment=AppointmentUpdate(estado=AppointmentStatus.CANCELADA),
        notification_event="rejected",
    )

    assert updated.estado == AppointmentStatus.CANCELADA
    assert rejected_calls == [(1001, 77, None, False)]
    assert len(db.added) == 1
    assert isinstance(db.added[0], Notification)
    assert db.added[0].usuario_id == 50
    assert "rechazada" in db.added[0].mensaje
    assert "La Barbería" in db.added[0].mensaje
    assert "Corte barba" in db.added[0].mensaje


def test_create_message_triggers_message_received(monkeypatch):
    from app.models import Appointment, Service, User
    from app.services.notification_orchestrator import orchestrator

    appointment = SimpleNamespace(cita_id=77, servicio_id=8)
    sender = SimpleNamespace(usuario_id=100)
    service = SimpleNamespace(servicio_id=8, establecimiento_id=88)
    db = _FakeDB({Appointment: appointment, User: sender, Service: service})

    calls = []
    monkeypatch.setattr(
        orchestrator,
        "on_message_received_sync",
        lambda _db, message_id, establishment_id: calls.append((message_id, establishment_id)),
    )

    message = MessageCreate(cita_id=77, emisor_id=100, contenido="hola")
    created = crud_messages.create_message(db, message)

    assert created.mensaje_id == 456
    assert calls == [(456, 88)]
