from types import SimpleNamespace

from app.crud import crud_plans


class _FakeQuery:
    def __init__(self, first_results):
        self._first_results = first_results

    def filter(self, *_args, **_kwargs):
        return self

    def first(self):
        return self._first_results.pop(0)


class _FakeDB:
    def __init__(self, first_results):
        self._first_results = first_results

    def query(self, _model):
        return _FakeQuery(self._first_results)


def test_initialize_default_plans_creates_and_seeds(monkeypatch):
    db = _FakeDB([None, None])
    created_plans = []
    seed_calls = []

    def _fake_create_plan(_db, plan):
        created = SimpleNamespace(plan_id=len(created_plans) + 1, nombre=plan.nombre)
        created_plans.append(created)
        return created

    def _fake_seed(_db, plan_id, feature_keys):
        seed_calls.append((plan_id, list(feature_keys)))
        return []

    monkeypatch.setattr(crud_plans, "create_plan", _fake_create_plan)

    import app.crud.crud_plan_features as cpf

    monkeypatch.setattr(cpf, "seed_plan_features", _fake_seed)

    result = crud_plans.initialize_default_plans(db)

    assert result["created"] is True
    assert result["free_plan_id"] == 1
    assert result["premium_plan_id"] == 2
    assert len(created_plans) == 2
    assert len(seed_calls) == 2
    assert len(seed_calls[0][1]) == 1
    assert len(seed_calls[1][1]) == 12


def test_initialize_default_plans_is_idempotent(monkeypatch):
    free = SimpleNamespace(plan_id=10, nombre="FREE")
    premium = SimpleNamespace(plan_id=20, nombre="PREMIUM")
    db = _FakeDB([free, premium])

    create_calls = []
    seed_calls = []

    def _fake_create_plan(_db, _plan):
        create_calls.append(True)
        return SimpleNamespace(plan_id=999)

    def _fake_seed(_db, plan_id, feature_keys):
        seed_calls.append((plan_id, list(feature_keys)))
        return []

    monkeypatch.setattr(crud_plans, "create_plan", _fake_create_plan)

    import app.crud.crud_plan_features as cpf

    monkeypatch.setattr(cpf, "seed_plan_features", _fake_seed)

    result = crud_plans.initialize_default_plans(db)

    assert result == {"created": False, "free_plan_id": 10, "premium_plan_id": 20}
    assert create_calls == []
    assert [call[0] for call in seed_calls] == [10, 20]
