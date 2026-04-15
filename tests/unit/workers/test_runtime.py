from saturn.bootstrap.settings import Settings
from saturn.workers.entrypoints import cpu, io, orchestrator
from saturn.workers.queues import CPU_QUEUES, IO_QUEUES, ORCHESTRATOR_QUEUES, queues_for_worker
from saturn.workers.runtime.broker import WorkerBroker
from saturn.workers.runtime.settings import WorkerRuntimeSettings


def test_queue_ownership_is_fixed() -> None:
    assert queues_for_worker("cpu") == ("parse", "embed")
    assert queues_for_worker("orchestrator") == ("reindex", "pipeline_remediation")
    assert queues_for_worker("io") == ("notion_sync", "export", "notifications")


def test_worker_broker_registers_subscriptions_without_business_imports() -> None:
    settings = WorkerRuntimeSettings(redis_url="redis://example:6379/0", queues=("parse", "embed"))
    broker = WorkerBroker(settings)

    state = broker.start()

    assert broker.started is True
    assert state.queues == ("parse", "embed")
    assert state.redis_url == "redis://example:6379/0"


def test_worker_entrypoints_return_owned_queues(monkeypatch) -> None:
    monkeypatch.setattr(
        "saturn.workers.runtime.settings.get_settings",
        lambda: Settings(redis_url="redis://example:6379/0"),
    )

    assert cpu.main() == CPU_QUEUES
    assert orchestrator.main() == ORCHESTRATOR_QUEUES
    assert io.main() == IO_QUEUES
