"""Google OAuth flow helpers."""

from dataclasses import dataclass
from urllib.parse import urlencode

from saturn.bootstrap.settings import Settings


@dataclass(frozen=True, slots=True)
class GoogleProfile:
    sub: str
    email: str
    display_name: str | None = None


def build_google_oauth_url(settings: Settings, state: str) -> str:
    if not settings.google_client_id or not settings.google_redirect_uri:
        return f"/api/v1/auth/google/callback?state={state}&test_mode=true"
    query = urlencode(
        {
            "client_id": settings.google_client_id,
            "redirect_uri": settings.google_redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }
    )
    return f"https://accounts.google.com/o/oauth2/v2/auth?{query}"


def profile_from_test_callback(email: str, name: str | None = None) -> GoogleProfile:
    return GoogleProfile(sub=f"test:{email.lower()}", email=email.lower(), display_name=name)
