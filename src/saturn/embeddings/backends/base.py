"""Embedding backend abstraction."""

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class EmbeddingVector:
    values: list[float]
    model_name: str
    dimensions: int


@runtime_checkable
class EmbeddingBackend(Protocol):
    model_name: str
    dimensions: int

    def embed(self, texts: list[str]) -> list[EmbeddingVector]: ...
