"""Authentication routes."""

from fastapi import APIRouter

from saturn.api.deps import DbSessionDep, SettingsDep
from saturn.identity.api_models import (
    GoogleOAuthCallbackRequest,
    GoogleOAuthStartResponse,
    SessionRead,
    UserRead,
)
from saturn.identity.google_oauth import build_google_oauth_url, profile_from_test_callback
from saturn.identity.service import IdentityService
from saturn.shared.ids import new_id

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.get("/google/start", response_model=GoogleOAuthStartResponse)
async def google_start(settings: SettingsDep) -> GoogleOAuthStartResponse:
    state = new_id()
    return GoogleOAuthStartResponse(
        authorization_url=build_google_oauth_url(settings, state),
        state=state,
    )


@router.post("/google/callback", response_model=SessionRead)
async def google_callback(payload: GoogleOAuthCallbackRequest, session: DbSessionDep) -> SessionRead:
    user_session = IdentityService(session).oauth_login_test_mode(
        profile_from_test_callback(payload.email, payload.name),
        org_name=payload.org_name,
        org_slug=payload.org_slug,
    )
    session.commit()
    user = IdentityService(session).get_user(user_session.user_id)
    return SessionRead(
        session_id=user_session.token,
        user=UserRead.model_validate(user),
        org_id=user_session.org_id,
    )
