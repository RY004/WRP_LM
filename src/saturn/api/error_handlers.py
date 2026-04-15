"""API exception and error response hooks."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from saturn.shared.exceptions import SaturnError


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(SaturnError)
    async def handle_saturn_error(_: Request, exc: SaturnError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
