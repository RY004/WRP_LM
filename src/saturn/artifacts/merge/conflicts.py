"""Artifact merge conflict contracts."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class MergeConflict:
    path: str
    base: Any
    left: Any
    right: Any
    reason: str
