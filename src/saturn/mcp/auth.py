"""MCP authentication helpers."""

from sqlalchemy.orm import Session

from saturn.access.context import AuthContext
from saturn.identity.service import IdentityService


def context_from_token(session: Session, token: str | None) -> AuthContext:
    if not token:
        raise PermissionError("MCP authentication required")
    user_session = IdentityService(session).get_session(token)
    if user_session is None:
        raise PermissionError("Invalid MCP session")
    return AuthContext(
        user_id=user_session.user_id,
        org_id=user_session.org_id,
        session_id=token,
    )
