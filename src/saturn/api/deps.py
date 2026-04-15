"""Shared FastAPI dependencies."""

from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from saturn.access.context import AuthContext
from saturn.bootstrap.container import ApplicationContainer
from saturn.bootstrap.settings import Settings, get_settings
from saturn.identity.service import IdentityService


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


def get_db_session(container: ContainerDep):
    session = container.session_factory()
    try:
        yield session
    finally:
        session.close()


DbSessionDep = Annotated[Session, Depends(get_db_session)]


def get_auth_context(
    session: DbSessionDep,
    authorization: Annotated[str | None, Header()] = None,
    x_saturn_session_id: Annotated[str | None, Header()] = None,
) -> AuthContext:
    token = x_saturn_session_id
    if token is None and authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1]
    if not token:
        return AuthContext.anonymous()
    user_session = IdentityService(session).get_session(token)
    if user_session is None:
        raise HTTPException(status_code=401, detail="Invalid session")
    return AuthContext(user_id=user_session.user_id, org_id=user_session.org_id, session_id=token)


AuthContextDep = Annotated[AuthContext, Depends(get_auth_context)]
