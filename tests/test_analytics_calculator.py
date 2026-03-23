from datetime import date, time
from types import SimpleNamespace

from app.models.analytics import DayOfWeek
from app.services import analytics_calculator


class _FakeQuery:
    def __init__(self, db, model):
        self.db = db
        self.model = model

    def filter(self, *_args, **_kwargs):
        return self

    def join(self, *_args, **_kwargs):
        return self

    def all(self):
        return self.db.all_map.get(self.model, [])

    def count(self):
        return self.db.count_map.get(self.model, 0)

    def delete(self, **_kwargs):
        self.db.deletes.append(self.model)
        return 0


class _FakeDB:
    def __init__(self, all_map=None, count_map=None):
        self.all_map = all_map or {}
        self.count_map = count_map or {}
        self.deletes = []
        self.commits = 0

    def query(self, model):
        return _FakeQuery(self, model)

    def commit(self):
        self.commits += 1


def test_recalculate_daily_occupancy_no_agenda_returns_zero(monkeypatch):
    db = _FakeDB()

    result = analytics_calculator.recalculate_daily_occupancy(
        db=db,
        establecimiento_id=1,
        target_date=date(2026, 3, 22),
    )

    assert result == {
        "slots_processed": 0,
        "metrics_created": 0,
        "suggestions_created": 0,
    }


def test_recalculate_daily_occupancy_creates_metrics_and_suggestions(monkeypatch):
    agenda = SimpleNamespace(
        establecimiento_id=1,
        dia_semana=DayOfWeek.DOMINGO,
        hora_inicio=time(9, 0),
        hora_fin=time(11, 0),
    )

    service = SimpleNamespace(precio=10)
    appointments = [
        SimpleNamespace(
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
            estado="CONFIRMADA",
            service=service,
        )
    ]

    from app.models import Agenda, Appointment

    db = _FakeDB(
        all_map={Agenda: [agenda], Appointment: appointments},
        count_map={},
    )

    created_metrics = []
    created_suggestions = []

    monkeypatch.setattr(
        analytics_calculator.crud_analytics,
        "create_occupancy_metric",
        lambda _db, metric: created_metrics.append(metric),
    )
    monkeypatch.setattr(
        analytics_calculator.crud_analytics,
        "create_suggestion",
        lambda _db, suggestion: created_suggestions.append(suggestion),
    )

    result = analytics_calculator.recalculate_daily_occupancy(
        db=db,
        establecimiento_id=1,
        target_date=date(2026, 3, 22),  # Sunday
        idle_threshold_percent=80.0,
    )

    assert result["slots_processed"] == 2
    assert result["metrics_created"] == 2
    assert result["suggestions_created"] >= 1
    assert len(created_metrics) == 2
    assert len(created_suggestions) >= 1
