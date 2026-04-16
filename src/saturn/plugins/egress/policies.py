"""Plugin egress policy service."""

from urllib.parse import urlparse

from sqlalchemy.orm import Session

from saturn.access.context import AuthContext
from saturn.access.policies import Permission, require_authenticated
from saturn.access.service import AccessService
from saturn.plugins.db_models import PluginEgressDecision, PluginEgressPolicy
from saturn.plugins.repository import PluginRepository


class PluginEgressPolicyService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = PluginRepository(session)
        self.access = AccessService(session)

    def create_policy(
        self,
        context: AuthContext,
        plugin_key: str,
        project_id: str | None,
        scheme: str,
        host: str,
        methods: list[str],
    ) -> PluginEgressPolicy:
        user_id = require_authenticated(context)
        if project_id is not None:
            self.access.require_project_permission(context, project_id, Permission.PROJECT_ADMIN)
        plugin = self.repository.get_plugin_by_key(plugin_key)
        if plugin is None:
            raise LookupError("Plugin not found")
        policy = self.repository.egress_policy(
            plugin.id, context.org_id or "", project_id, scheme.lower(), host.lower()
        )
        if policy is None:
            policy = self.repository.add(
                PluginEgressPolicy(
                    plugin_id=plugin.id,
                    org_id=context.org_id or "",
                    project_id=project_id,
                    scheme=scheme.lower(),
                    host=host.lower(),
                    methods=[method.upper() for method in methods],
                    created_by_user_id=user_id,
                )
            )
        else:
            policy.methods = [method.upper() for method in methods]
            policy.enabled = True
        self.session.flush()
        return policy

    def evaluate(
        self,
        context: AuthContext,
        plugin_key: str,
        project_id: str,
        url: str,
        method: str,
        execution_id: str | None = None,
    ) -> tuple[bool, str]:
        require_authenticated(context)
        self.access.require_project_permission(context, project_id, Permission.PROJECT_READ)
        plugin = self.repository.get_plugin_by_key(plugin_key)
        if plugin is None:
            raise LookupError("Plugin not found")
        parsed = urlparse(url)
        scheme = (parsed.scheme or "").lower()
        host = (parsed.hostname or "").lower()
        method = method.upper()
        allowed = False
        reason = "No matching egress policy"
        if scheme not in {"https", "http"} or not host:
            reason = "Unsupported or malformed outbound URL"
        else:
            for policy in self.repository.matching_egress_policies(
                plugin.id, context.org_id or "", project_id, scheme, host
            ):
                methods = {item.upper() for item in policy.methods}
                if "*" in methods or method in methods:
                    allowed = True
                    reason = "Allowed by plugin egress policy"
                    break
        self.repository.add(
            PluginEgressDecision(
                plugin_id=plugin.id,
                execution_id=execution_id,
                org_id=context.org_id or "",
                project_id=project_id,
                url=url,
                method=method,
                allowed=allowed,
                reason=reason,
            )
        )
        self.session.flush()
        return allowed, reason
