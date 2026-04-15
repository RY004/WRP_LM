"""Worker broker wiring."""

from dataclasses import dataclass

from saturn.shared.time import utc_now
from saturn.workers.runtime.settings import WorkerRuntimeSettings


@dataclass(frozen=True, slots=True)
class QueueSubscription:
    name: str


@dataclass(frozen=True, slots=True)
class WorkerRuntimeState:
    redis_url: str
    queues: tuple[str, ...]
    started_at: str


class WorkerBroker:
    def __init__(self, settings: WorkerRuntimeSettings) -> None:
        self.settings = settings
        self.subscriptions = tuple(QueueSubscription(queue) for queue in settings.queues)
        self.started = False

    def start(self) -> WorkerRuntimeState:
        self.started = True
        return WorkerRuntimeState(
            redis_url=self.settings.redis_url,
            queues=tuple(subscription.name for subscription in self.subscriptions),
            started_at=utc_now().isoformat(),
        )
