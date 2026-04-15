"""API exception and error response hooks."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from saturn.shared.exceptions import SaturnError


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(SaturnError)
    async def handle_saturn_error(_: Request, exc: SaturnError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_error(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(PermissionError)
    async def handle_permission_error(_: Request, exc: PermissionError) -> JSONResponse:
        detail = str(exc) or "Forbidden"
        status_code = 401 if "Authentication required" in detail else 403
        return JSONResponse(status_code=status_code, content={"detail": detail})

    @app.exception_handler(LookupError)
    async def handle_lookup_error(_: Request, exc: LookupError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc) or "Not found"})

    @app.exception_handler(ValueError)
    async def handle_value_error(_: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})
