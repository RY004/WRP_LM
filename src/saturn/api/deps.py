"""Shared FastAPI dependencies."""

from saturn.bootstrap.container import ApplicationContainer
from saturn.bootstrap.settings import Settings, get_settings


def get_container() -> ApplicationContainer:
    return ApplicationContainer(settings=get_settings())


def get_app_settings() -> Settings:
    return get_settings()
