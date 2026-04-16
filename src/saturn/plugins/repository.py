"""Repository layer for plugins."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from saturn.plugins.db_models import (
    Plugin,
    PluginCapability,
    PluginEgressDecision,
    PluginEgressPolicy,
    PluginExecution,
    PluginInstallation,
    PluginVersion,
    VSCodeTokenExchange,
    VSCodeWorkspaceSession,
)


class PluginRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, row):
        self.session.add(row)
        return row

    def get_plugin_by_key(self, key: str) -> Plugin | None:
        return self.session.scalar(select(Plugin).where(Plugin.key == key))

    def list_plugins(self) -> list[Plugin]:
        return list(self.session.scalars(select(Plugin).order_by(Plugin.key)))

    def get_version(self, plugin_id: str, version: str) -> PluginVersion | None:
        return self.session.scalar(
            select(PluginVersion).where(
                PluginVersion.plugin_id == plugin_id,
                PluginVersion.version == version,
            )
        )

    def get_version_by_id(self, version_id: str) -> PluginVersion | None:
        return self.session.get(PluginVersion, version_id)

    def list_capabilities(self, version_id: str) -> list[PluginCapability]:
        return list(
            self.session.scalars(
                select(PluginCapability)
                .where(PluginCapability.plugin_version_id == version_id)
                .order_by(PluginCapability.capability)
            )
        )

    def get_capability(self, version_id: str, capability: str) -> PluginCapability | None:
        return self.session.scalar(
            select(PluginCapability).where(
                PluginCapability.plugin_version_id == version_id,
                PluginCapability.capability == capability,
            )
        )

    def get_installation(
        self, plugin_id: str, org_id: str, project_id: str | None
    ) -> PluginInstallation | None:
        return self.session.scalar(
            select(PluginInstallation).where(
                PluginInstallation.plugin_id == plugin_id,
                PluginInstallation.org_id == org_id,
                PluginInstallation.project_id == project_id,
            )
        )

    def list_installations(self, org_id: str, project_id: str | None = None) -> list[PluginInstallation]:
        query = select(PluginInstallation).where(PluginInstallation.org_id == org_id)
        if project_id is not None:
            query = query.where(PluginInstallation.project_id.in_([project_id, None]))
        return list(self.session.scalars(query.order_by(PluginInstallation.installed_at.desc())))

    def get_installation_by_id(self, installation_id: str) -> PluginInstallation | None:
        return self.session.get(PluginInstallation, installation_id)

    def find_enabled_installation(
        self, plugin_id: str, org_id: str, project_id: str
    ) -> PluginInstallation | None:
        project_install = self.get_installation(plugin_id, org_id, project_id)
        if project_install and project_install.enabled:
            return project_install
        org_install = self.get_installation(plugin_id, org_id, None)
        if org_install and org_install.enabled:
            return org_install
        return None

    def egress_policy(
        self, plugin_id: str, org_id: str, project_id: str | None, scheme: str, host: str
    ) -> PluginEgressPolicy | None:
        return self.session.scalar(
            select(PluginEgressPolicy).where(
                PluginEgressPolicy.plugin_id == plugin_id,
                PluginEgressPolicy.org_id == org_id,
                PluginEgressPolicy.project_id == project_id,
                PluginEgressPolicy.scheme == scheme,
                PluginEgressPolicy.host == host,
            )
        )

    def matching_egress_policies(
        self, plugin_id: str, org_id: str, project_id: str, scheme: str, host: str
    ) -> list[PluginEgressPolicy]:
        return list(
            self.session.scalars(
                select(PluginEgressPolicy).where(
                    PluginEgressPolicy.plugin_id == plugin_id,
                    PluginEgressPolicy.org_id == org_id,
                    PluginEgressPolicy.project_id.in_([project_id, None]),
                    PluginEgressPolicy.scheme == scheme,
                    PluginEgressPolicy.host == host,
                    PluginEgressPolicy.enabled.is_(True),
                )
            )
        )

    def get_token_exchange(self, exchange_token: str) -> VSCodeTokenExchange | None:
        return self.session.scalar(
            select(VSCodeTokenExchange).where(VSCodeTokenExchange.exchange_token == exchange_token)
        )

    def get_workspace_session(
        self, project_id: str, workspace_uri: str, user_id: str
    ) -> VSCodeWorkspaceSession | None:
        return self.session.scalar(
            select(VSCodeWorkspaceSession).where(
                VSCodeWorkspaceSession.project_id == project_id,
                VSCodeWorkspaceSession.workspace_uri == workspace_uri,
                VSCodeWorkspaceSession.user_id == user_id,
            )
        )
