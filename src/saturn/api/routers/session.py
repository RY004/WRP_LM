"""Session routes."""

from fastapi import APIRouter

from saturn.api.deps import AuthContextDep, DbSessionDep
from saturn.identity.api_models import SessionRead, UserRead
from saturn.identity.service import IdentityService

router = APIRouter(prefix="/api/v1/session", tags=["session"])


@router.get("", response_model=SessionRead)
async def get_session(context: AuthContextDep, session: DbSessionDep) -> SessionRead:
    if not context.session_id or not context.user_id or not context.org_id:
        raise PermissionError("Authentication required")
    user = IdentityService(session).get_user(context.user_id)
    return SessionRead(
        session_id=context.session_id,
        user=UserRead.model_validate(user),
        org_id=context.org_id,
    )
