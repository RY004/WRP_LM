"""Filesystem-backed storage for local development and CI."""

from pathlib import Path, PurePosixPath

from saturn.storage.base import BlobDescriptor
from saturn.shared.exceptions import StorageError


class FilesystemStorage:
    scheme = "file"

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _path_for(self, key: str) -> Path:
        normalized = PurePosixPath(key)
        if not key or normalized.is_absolute() or ".." in normalized.parts:
            raise StorageError(f"Invalid blob key: {key!r}")
        path = (self.root / Path(*normalized.parts)).resolve()
        if self.root not in path.parents and path != self.root:
            raise StorageError(f"Blob key escapes storage root: {key!r}")
        return path

    def write_bytes(self, key: str, payload: bytes) -> BlobDescriptor:
        path = self._path_for(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
        return BlobDescriptor(uri=path.as_uri(), key=key, size_bytes=len(payload))

    def read_bytes(self, key: str) -> bytes:
        return self._path_for(key).read_bytes()

    def exists(self, key: str) -> bool:
        return self._path_for(key).exists()

    def delete(self, key: str) -> None:
        self._path_for(key).unlink(missing_ok=True)
