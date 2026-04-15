from pathlib import Path

import pytest
from pydantic import ValidationError

from saturn.bootstrap.container import ApplicationContainer
from saturn.bootstrap.settings import Settings
from saturn.storage.filesystem import FilesystemStorage


def test_settings_normalize_empty_optional_values(reset_settings_cache: None) -> None:
    settings = Settings(storage_s3_endpoint="", google_client_id="")

    assert settings.storage_s3_endpoint is None
    assert settings.google_client_id is None
    assert settings.log_level == "INFO"


def test_s3_storage_requires_bucket() -> None:
    with pytest.raises(ValidationError):
        Settings(storage_backend="s3")


def test_container_builds_configured_filesystem_storage(tmp_path: Path) -> None:
    settings = Settings(storage_filesystem_root=tmp_path)
    container = ApplicationContainer(settings=settings)

    assert isinstance(container.storage, FilesystemStorage)
    assert container.storage is container.storage
