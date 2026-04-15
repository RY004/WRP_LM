"""FastAPI application factory for Saturn."""

from fastapi import FastAPI

from saturn.api.error_handlers import register_error_handlers


def create_app() -> FastAPI:
    app = FastAPI(title="Saturn")

    @app.get("/healthz", tags=["system"])
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    register_error_handlers(app)
    return app
