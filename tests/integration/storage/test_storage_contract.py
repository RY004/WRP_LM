from pathlib import Path

import pytest

from saturn.shared.exceptions import StorageError
from saturn.storage.filesystem import FilesystemStorage


def test_filesystem_storage_round_trip(tmp_path: Path) -> None:
    storage = FilesystemStorage(tmp_path)

    descriptor = storage.write_bytes("documents/source.txt", b"hello saturn")

    assert descriptor.key == "documents/source.txt"
    assert descriptor.uri.startswith("file://")
    assert descriptor.size_bytes == 12
    assert storage.exists("documents/source.txt")
    assert storage.read_bytes("documents/source.txt") == b"hello saturn"

    storage.delete("documents/source.txt")
    assert not storage.exists("documents/source.txt")


def test_filesystem_storage_rejects_path_traversal(tmp_path: Path) -> None:
    storage = FilesystemStorage(tmp_path)

    with pytest.raises(StorageError):
        storage.write_bytes("../escape.txt", b"nope")
