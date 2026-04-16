"""Plugin registry and installation service."""

from sqlalchemy.orm import Session

from saturn.access.context import AuthContext
from saturn.access.policies import Permission, require_authenticated
from saturn.access.service import AccessService
from saturn.plugins.api_models import PluginCapabilityDecl
from saturn.plugins.db_models import Plugin, PluginCapability, PluginInstallation, PluginVersion
from saturn.plugins.repository import PluginRepository


class PluginRegistryService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = PluginRepository(session)
        self.access = AccessService(session)

    def register(
        self,
        context: AuthContext,
        key: str,
        name: str,
        description: str | None,
        version: str,
        entrypoint: str,
        manifest: dict,
        capabilities: list[PluginCapabilityDecl],
    ) -> tuple[Plugin, PluginVersion]:
        user_id = require_authenticated(context)
        plugin = self.repository.get_plugin_by_key(key)
        if plugin is None:
            plugin = self.repository.add(
                Plugin(
                    key=key,
                    name=name,
                    description=description,
                    owner_org_id=context.org_id,
                    created_by_user_id=user_id,
                )
            )
            self.session.flush()
        else:
            plugin.name = name
            plugin.description = description
        plugin_version = self.repository.get_version(plugin.id, version)
        if plugin_version is None:
            plugin_version = self.repository.add(
                PluginVersion(
                    plugin_id=plugin.id,
                    version=version,
                    entrypoint=entrypoint,
                    manifest=manifest,
                )
            )
            self.session.flush()
        else:
            plugin_version.entrypoint = entrypoint
            plugin_version.manifest = manifest
        existing = {item.capability for item in self.repository.list_capabilities(plugin_version.id)}
        for declared in capabilities:
            if declared.capability in existing:
                continue
            self.repository.add(
                PluginCapability(
                    plugin_version_id=plugin_version.id,
                    capability=declared.capability,
                    domain=declared.domain,
                    permissions=declared.permissions,
                    metadata_=declared.metadata,
                )
            )
        self.session.flush()
        return plugin, plugin_version

    def install(
        self,
        context: AuthContext,
        plugin_key: str,
        version: str,
        project_id: str | None,
        enabled: bool,
    ) -> PluginInstallation:
        user_id = require_authenticated(context)
        if project_id is not None:
            self.access.require_project_permission(context, project_id, Permission.PROJECT_ADMIN)
        elif not context.org_id:
            raise PermissionError("Authentication required")
        plugin = self._require_plugin(plugin_key)
        plugin_version = self.repository.get_version(plugin.id, version)
        if plugin_version is None:
            raise LookupError("Plugin version not found")
        installation = self.repository.get_installation(plugin.id, context.org_id or "", project_id)
        if installation is None:
            installation = self.repository.add(
                PluginInstallation(
                    plugin_id=plugin.id,
                    plugin_version_id=plugin_version.id,
                    org_id=context.org_id or "",
                    project_id=project_id,
                    enabled=enabled,
                    installed_by_user_id=user_id,
                )
            )
        else:
            installation.plugin_version_id = plugin_version.id
            installation.enabled = enabled
        self.session.flush()
        return installation

    def set_enabled(self, context: AuthContext, installation_id: str, enabled: bool) -> PluginInstallation:
        require_authenticated(context)
        installation = self.repository.get_installation_by_id(installation_id)
        if installation is None:
            raise LookupError("Plugin installation not found")
        if installation.project_id is not None:
            self.access.require_project_permission(
                context, installation.project_id, Permission.PROJECT_ADMIN
            )
        elif installation.org_id != context.org_id:
            raise PermissionError("Insufficient org access")
        installation.enabled = enabled
        self.session.flush()
        return installation

    def list_plugins(self) -> list[Plugin]:
        return self.repository.list_plugins()

    def list_installations(self, context: AuthContext, project_id: str | None = None) -> list[PluginInstallation]:
        require_authenticated(context)
        if project_id is not None:
            self.access.require_project_permission(context, project_id, Permission.PROJECT_READ)
        return self.repository.list_installations(context.org_id or "", project_id)

    def _require_plugin(self, key: str) -> Plugin:
        plugin = self.repository.get_plugin_by_key(key)
        if plugin is None:
            raise LookupError("Plugin not found")
        return plugin
