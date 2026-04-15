"""Idempotency context middleware."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class IdempotencyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request.state.idempotency_key = request.headers.get("Idempotency-Key")
        response = await call_next(request)
        if request.state.idempotency_key:
            response.headers["Idempotency-Key"] = request.state.idempotency_key
        return response
