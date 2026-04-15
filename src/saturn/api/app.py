"""FastAPI application factory for Saturn."""

from fastapi import FastAPI

from saturn.api.middleware.auth import AuthenticationContextMiddleware
from saturn.api.middleware.idempotency import IdempotencyMiddleware
from saturn.api.middleware.request_context import RequestContextMiddleware
from saturn.api.routers import (
    artifacts,
    auth,
    comments,
    documents,
    memberships,
    notion,
    pipeline,
    plugins,
    projects,
    retrieval,
    session,
)
from saturn.api.error_handlers import register_error_handlers
from saturn.bootstrap.container import ApplicationContainer
from saturn.bootstrap.logging import configure_logging
from saturn.bootstrap.settings import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(title=settings.app_name)
    app.state.container = ApplicationContainer(settings=settings)

    app.add_middleware(IdempotencyMiddleware)
    app.add_middleware(AuthenticationContextMiddleware)
    app.add_middleware(RequestContextMiddleware)

    for router in (
        auth.router,
        session.router,
        projects.router,
        memberships.router,
        artifacts.router,
        comments.router,
        documents.router,
        retrieval.router,
        pipeline.router,
        notion.router,
        plugins.router,
    ):
        app.include_router(router)

    @app.get("/healthz", tags=["system"])
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok", "service": settings.app_name, "environment": settings.app_env}

    @app.get("/readyz", tags=["system"])
    async def readiness() -> dict[str, str]:
        return {"status": "ready"}

    register_error_handlers(app)
    return app
