"""I/O worker entrypoint."""

from saturn.workers.queues import IO_QUEUES
from saturn.workers.runtime.broker import WorkerBroker
from saturn.workers.runtime.settings import WorkerRuntimeSettings


def main() -> tuple[str, ...]:
    WorkerBroker(WorkerRuntimeSettings.from_settings(queues=IO_QUEUES)).start()
    return IO_QUEUES


if __name__ == "__main__":
    print(",".join(main()))
