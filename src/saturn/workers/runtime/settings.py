"""Worker runtime settings."""

from dataclasses import dataclass

from saturn.bootstrap.settings import Settings, get_settings
from saturn.workers.queues import ALL_QUEUES


@dataclass(slots=True)
class WorkerRuntimeSettings:
    redis_url: str
    queues: tuple[str, ...] = ALL_QUEUES
    poll_interval_seconds: float = 1.0

    @classmethod
    def from_settings(
        cls, settings: Settings | None = None, queues: tuple[str, ...] = ALL_QUEUES
    ) -> "WorkerRuntimeSettings":
        settings = settings or get_settings()
        return cls(redis_url=settings.redis_url, queues=queues)
