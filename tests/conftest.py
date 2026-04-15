"""Shared test fixtures."""

import pytest

from saturn.bootstrap.settings import get_settings


@pytest.fixture()
def reset_settings_cache() -> None:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
