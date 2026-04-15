"""Shared FastAPI dependencies."""

from cortex.bootstrap.container import ApplicationContainer
from cortex.bootstrap.settings import Settings, get_settings


def get_container() -> ApplicationContainer:
    return ApplicationContainer(settings=get_settings())


def get_app_settings() -> Settings:
    return get_settings()
