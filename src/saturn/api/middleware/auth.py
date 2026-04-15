"""Phase-1 authentication context middleware.

Full authentication and authorization land in phase 2. This middleware only
captures request auth hints so later dependencies have one stable place to read
from.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class AuthenticationContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        authorization = request.headers.get("Authorization")
        request.state.authorization = authorization
        request.state.api_key = request.headers.get("X-Saturn-Api-Key")
        return await call_next(request)
