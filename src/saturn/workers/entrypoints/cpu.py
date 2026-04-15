"""CPU worker entrypoint."""

from saturn.workers.queues import CPU_QUEUES
from saturn.workers.runtime.broker import WorkerBroker
from saturn.workers.runtime.settings import WorkerRuntimeSettings


def main() -> tuple[str, ...]:
    WorkerBroker(WorkerRuntimeSettings.from_settings(queues=CPU_QUEUES)).start()
    return CPU_QUEUES


if __name__ == "__main__":
    print(",".join(main()))
