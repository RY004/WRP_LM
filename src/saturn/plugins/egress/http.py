"""HTTP egress helper that records allow/deny decisions before network access."""

from typing import Any

import httpx
from sqlalchemy.orm import Session

from saturn.access.context import AuthContext
from saturn.plugins.egress.allowlist import PluginEgressAllowlist


class PluginHttpEgressClient:
    def __init__(self, session: Session, timeout_seconds: float = 5.0) -> None:
        self.allowlist = PluginEgressAllowlist(session)
        self.timeout_seconds = timeout_seconds

    def request(
        self,
        context: AuthContext,
        plugin_key: str,
        project_id: str,
        method: str,
        url: str,
        execution_id: str | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        self.allowlist.require_allowed(
            context, plugin_key, project_id, url, method, execution_id=execution_id
        )
        with httpx.Client(timeout=self.timeout_seconds, follow_redirects=False) as client:
            return client.request(method, url, **kwargs)
