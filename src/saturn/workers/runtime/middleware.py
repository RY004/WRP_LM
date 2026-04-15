"""Worker middleware primitives."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

from saturn.shared.ids import new_id

T = TypeVar("T")


@dataclass(slots=True)
class JobContext:
    queue: str
    job_id: str


def with_job_context(queue: str, fn: Callable[[JobContext], T]) -> T:
    return fn(JobContext(queue=queue, job_id=new_id()))
