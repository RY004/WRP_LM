"""Shared FastAPI dependencies."""

from typing import Annotated

from fastapi import Depends, Request

from saturn.bootstrap.container import ApplicationContainer
from saturn.bootstrap.settings import Settings, get_settings


def get_container(request: Request) -> ApplicationContainer:
    container = getattr(request.app.state, "container", None)
    if container is None:
        container = ApplicationContainer(settings=get_settings())
        request.app.state.container = container
    return container


def get_app_settings() -> Settings:
    return get_settings()


ContainerDep = Annotated[ApplicationContainer, Depends(get_container)]
SettingsDep = Annotated[Settings, Depends(get_app_settings)]
