"""Blob storage abstraction."""

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(slots=True)
class BlobDescriptor:
    uri: str
    key: str
    size_bytes: int | None = None
    etag: str | None = None


@runtime_checkable
class StorageBackend(Protocol):
    scheme: str

    def write_bytes(self, key: str, payload: bytes) -> BlobDescriptor: ...

    def read_bytes(self, key: str) -> bytes: ...

    def exists(self, key: str) -> bool: ...

    def delete(self, key: str) -> None: ...
