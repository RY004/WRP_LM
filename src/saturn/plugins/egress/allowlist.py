"""Outbound allowlist facade."""

from sqlalchemy.orm import Session

from saturn.access.context import AuthContext
from saturn.plugins.egress.policies import PluginEgressPolicyService


class EgressDeniedError(PermissionError):
    """Raised when plugin egress is not explicitly allowed."""


class PluginEgressAllowlist:
    def __init__(self, session: Session) -> None:
        self.policies = PluginEgressPolicyService(session)

    def require_allowed(
        self,
        context: AuthContext,
        plugin_key: str,
        project_id: str,
        url: str,
        method: str,
        execution_id: str | None = None,
    ) -> None:
        allowed, reason = self.policies.evaluate(
            context, plugin_key, project_id, url, method, execution_id
        )
        if not allowed:
            raise EgressDeniedError(reason)
