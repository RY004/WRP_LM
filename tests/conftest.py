"""Shared test fixtures."""

import pytest

from saturn.bootstrap.settings import get_settings
from tests.fixtures.phase2 import phase2_app, phase2_session_factory  # noqa: F401


@pytest.fixture()
def reset_settings_cache() -> None:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
