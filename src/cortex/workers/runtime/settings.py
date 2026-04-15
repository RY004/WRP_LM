"""Worker runtime settings scaffold."""

from dataclasses import dataclass


@dataclass(slots=True)
class WorkerRuntimeSettings:
    redis_url: str
