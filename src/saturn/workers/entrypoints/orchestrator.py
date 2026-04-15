"""Orchestrator worker entrypoint."""

from saturn.workers.queues import ORCHESTRATOR_QUEUES
from saturn.workers.runtime.broker import WorkerBroker
from saturn.workers.runtime.settings import WorkerRuntimeSettings


def main() -> tuple[str, ...]:
    WorkerBroker(WorkerRuntimeSettings.from_settings(queues=ORCHESTRATOR_QUEUES)).start()
    return ORCHESTRATOR_QUEUES


if __name__ == "__main__":
    print(",".join(main()))
