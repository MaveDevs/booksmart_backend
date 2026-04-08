from concurrent.futures import ThreadPoolExecutor


class _FakeDB:
    pass


def test_sync_wrapper_runs_in_worker_thread_without_event_loop(monkeypatch):
    from app.services.notification_orchestrator import NotificationOrchestrator

    orchestrator = NotificationOrchestrator()
    called = {"value": False}

    async def fake_on_appointment_created(_db, _appointment_id, _establishment_id):
        called["value"] = True

    monkeypatch.setattr(
        orchestrator,
        "on_appointment_created",
        fake_on_appointment_created,
    )

    def worker():
        orchestrator.on_appointment_created_sync(_FakeDB(), 1, 1)

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(worker)
        future.result(timeout=5)

    assert called["value"] is True
