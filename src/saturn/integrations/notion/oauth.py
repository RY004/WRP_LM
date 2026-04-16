"""Notion OAuth helpers."""

import base64
from dataclasses import dataclass
from urllib.parse import urlencode

from saturn.shared.ids import new_id


@dataclass(frozen=True, slots=True)
class NotionTokenPayload:
    access_token: str
    workspace_id: str
    workspace_name: str
    bot_id: str | None = None
    refresh_token: str | None = None
    expires_in_seconds: int | None = None


def new_oauth_state() -> str:
    return new_id()


def build_authorization_url(client_id: str | None, redirect_uri: str | None, state: str) -> str:
    params = {
        "client_id": client_id or "local-dev-client",
        "response_type": "code",
        "owner": "user",
        "redirect_uri": redirect_uri or "http://localhost/notion/callback",
        "state": state,
    }
    return f"https://api.notion.com/v1/oauth/authorize?{urlencode(params)}"


def protect_token(token: str) -> str:
    return base64.urlsafe_b64encode(token.encode("utf-8")).decode("ascii")


def reveal_token(value: str) -> str:
    return base64.urlsafe_b64decode(value.encode("ascii")).decode("utf-8")
