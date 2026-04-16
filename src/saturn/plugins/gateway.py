"""Governed plugin execution gateway."""

from sqlalchemy.orm import Session

from saturn.access.context import AuthContext
from saturn.access.policies import Permission, require_authenticated
from saturn.access.service import AccessService
from saturn.plugins.db_models import PluginExecution
from saturn.plugins.internal_api import InternalPluginAPI
from saturn.plugins.repository import PluginRepository
from saturn.shared.time import utc_now


PERMISSION_BY_CAPABILITY_PREFIX = {
    "pipeline.get": Permission.PIPELINE_READ,
    "pipeline.handoff": Permission.PIPELINE_READ,
    "pipeline.add_decision": Permission.PIPELINE_ADVANCE,
    "pipeline.advance": Permission.PIPELINE_ADVANCE,
    "rag.query": Permission.PROJECT_READ,
    "wiki.list": Permission.PROJECT_READ,
    "wiki.get": Permission.PROJECT_READ,
    "wiki.create": Permission.PROJECT_WRITE,
    "wiki.update": Permission.PROJECT_WRITE,
}


class PluginGateway:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = PluginRepository(session)
        self.access = AccessService(session)
        self.internal_api = InternalPluginAPI(session)

    def execute(
        self,
        context: AuthContext,
        plugin_key: str,
        project_id: str,
        capability: str,
        payload: dict,
    ) -> tuple[PluginExecution, dict]:
        user_id = require_authenticated(context)
        if not context.org_id:
            raise PermissionError("Authentication required")
        plugin = self.repository.get_plugin_by_key(plugin_key)
        if plugin is None:
            raise LookupError("Plugin not found")
        installation = self.repository.find_enabled_installation(plugin.id, context.org_id, project_id)
        if installation is None:
            raise PermissionError("Plugin is not enabled for this project")
        plugin_version = self.repository.get_version_by_id(installation.plugin_version_id)
        if plugin_version is None:
            raise LookupError("Plugin version not found")
        capability_row = self.repository.get_capability(plugin_version.id, capability)
        if capability_row is None:
            raise PermissionError("Plugin capability is not declared")
        self._require_capability_permission(context, project_id, capability)
        action = capability.split(".", 1)[1] if "." in capability else capability
        execution = self.repository.add(
            PluginExecution(
                plugin_id=plugin.id,
                plugin_version_id=plugin_version.id,
                installation_id=installation.id,
                org_id=context.org_id,
                project_id=project_id,
                user_id=user_id,
                capability=capability,
                request=payload,
            )
        )
        self.session.flush()
        try:
            result = self.internal_api.dispatch(
                context, project_id, capability_row.domain, action, payload
            )
        except Exception as exc:
            execution.status = "failed"
            execution.error = str(exc)
            execution.finished_at = utc_now()
            self.session.flush()
            raise
        execution.status = "succeeded"
        execution.response_summary = self._summarize_result(result)
        execution.finished_at = utc_now()
        self.session.flush()
        return execution, result

    def _require_capability_permission(
        self, context: AuthContext, project_id: str, capability: str
    ) -> None:
        permission = PERMISSION_BY_CAPABILITY_PREFIX.get(capability)
        if permission is None:
            raise PermissionError("Unsupported plugin capability")
        self.access.require_project_permission(context, project_id, permission)

    def _summarize_result(self, result: dict) -> dict:
        return {
            "keys": sorted(result.keys()),
            "result_count": len(result.get("results", [])) if isinstance(result.get("results"), list) else None,
        }
