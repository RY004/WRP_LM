"""Plugins and audit schema."""

from alembic import op
import sqlalchemy as sa

revision = "0008_plugins_audit"
down_revision = "0007_notion_sync"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "plugins",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("key", sa.String(length=120), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("owner_org_id", sa.String(length=36), sa.ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("created_by_user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("key", name="uq_plugins_key"),
    )
    op.create_index("ix_plugins_key", "plugins", ["key"])
    op.create_table(
        "plugin_versions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("plugin_id", sa.String(length=36), sa.ForeignKey("plugins.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.String(length=64), nullable=False),
        sa.Column("entrypoint", sa.String(length=255), nullable=False, server_default="internal"),
        sa.Column("manifest", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("plugin_id", "version", name="uq_plugin_versions_plugin_version"),
    )
    op.create_index("ix_plugin_versions_plugin_id", "plugin_versions", ["plugin_id"])
    op.create_table(
        "plugin_capabilities",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("plugin_version_id", sa.String(length=36), sa.ForeignKey("plugin_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("capability", sa.String(length=120), nullable=False),
        sa.Column("domain", sa.String(length=32), nullable=False),
        sa.Column("permissions", sa.JSON(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.UniqueConstraint("plugin_version_id", "capability", name="uq_plugin_capabilities_version_capability"),
    )
    op.create_index("ix_plugin_capabilities_plugin_version_id", "plugin_capabilities", ["plugin_version_id"])
    op.create_table(
        "plugin_installations",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("plugin_id", sa.String(length=36), sa.ForeignKey("plugins.id", ondelete="CASCADE"), nullable=False),
        sa.Column("plugin_version_id", sa.String(length=36), sa.ForeignKey("plugin_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("org_id", sa.String(length=36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("project_id", sa.String(length=36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("installed_by_user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("installed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("plugin_id", "org_id", "project_id", name="uq_plugin_installations_scope"),
    )
    op.create_index("ix_plugin_installations_plugin_id", "plugin_installations", ["plugin_id"])
    op.create_index("ix_plugin_installations_org_id", "plugin_installations", ["org_id"])
    op.create_index("ix_plugin_installations_project_id", "plugin_installations", ["project_id"])
    op.create_table(
        "plugin_executions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("plugin_id", sa.String(length=36), sa.ForeignKey("plugins.id", ondelete="CASCADE"), nullable=False),
        sa.Column("plugin_version_id", sa.String(length=36), sa.ForeignKey("plugin_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("installation_id", sa.String(length=36), sa.ForeignKey("plugin_installations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("org_id", sa.String(length=36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("project_id", sa.String(length=36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("capability", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="started"),
        sa.Column("request", sa.JSON(), nullable=False),
        sa.Column("response_summary", sa.JSON(), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
    )
    for column in ("plugin_id", "installation_id", "org_id", "project_id", "user_id"):
        op.create_index(f"ix_plugin_executions_{column}", "plugin_executions", [column])
    op.create_table(
        "plugin_egress_policies",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("plugin_id", sa.String(length=36), sa.ForeignKey("plugins.id", ondelete="CASCADE"), nullable=False),
        sa.Column("org_id", sa.String(length=36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("project_id", sa.String(length=36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=True),
        sa.Column("scheme", sa.String(length=16), nullable=False, server_default="https"),
        sa.Column("host", sa.String(length=255), nullable=False),
        sa.Column("methods", sa.JSON(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_by_user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("plugin_id", "org_id", "project_id", "scheme", "host", name="uq_plugin_egress_policy_scope"),
    )
    op.create_index("ix_plugin_egress_policies_plugin_id", "plugin_egress_policies", ["plugin_id"])
    op.create_index("ix_plugin_egress_policies_org_id", "plugin_egress_policies", ["org_id"])
    op.create_table(
        "plugin_egress_decisions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("plugin_id", sa.String(length=36), sa.ForeignKey("plugins.id", ondelete="CASCADE"), nullable=False),
        sa.Column("execution_id", sa.String(length=36), sa.ForeignKey("plugin_executions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("org_id", sa.String(length=36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("project_id", sa.String(length=36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("method", sa.String(length=16), nullable=False),
        sa.Column("allowed", sa.Boolean(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_plugin_egress_decisions_plugin_id", "plugin_egress_decisions", ["plugin_id"])
    op.create_index("ix_plugin_egress_decisions_org_id", "plugin_egress_decisions", ["org_id"])
    op.create_table(
        "vscode_token_exchanges",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("exchange_token", sa.String(length=128), nullable=False),
        sa.Column("session_token", sa.String(length=128), nullable=False),
        sa.Column("org_id", sa.String(length=36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("exchange_token", name="uq_vscode_token_exchanges_exchange_token"),
    )
    op.create_index("ix_vscode_token_exchanges_exchange_token", "vscode_token_exchanges", ["exchange_token"])
    op.create_index("ix_vscode_token_exchanges_session_token", "vscode_token_exchanges", ["session_token"])
    op.create_index("ix_vscode_token_exchanges_org_id", "vscode_token_exchanges", ["org_id"])
    op.create_index("ix_vscode_token_exchanges_user_id", "vscode_token_exchanges", ["user_id"])
    op.create_table(
        "vscode_workspace_sessions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("project_id", sa.String(length=36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("org_id", sa.String(length=36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("workspace_uri", sa.Text(), nullable=False),
        sa.Column("agent_id", sa.String(length=120), nullable=True),
        sa.Column("capabilities", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_in_seconds", sa.Integer(), nullable=False, server_default="86400"),
        sa.UniqueConstraint("project_id", "workspace_uri", "user_id", name="uq_vscode_workspace_sessions_scope"),
    )
    op.create_index("ix_vscode_workspace_sessions_project_id", "vscode_workspace_sessions", ["project_id"])
    op.create_index("ix_vscode_workspace_sessions_org_id", "vscode_workspace_sessions", ["org_id"])
    op.create_index("ix_vscode_workspace_sessions_user_id", "vscode_workspace_sessions", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_vscode_workspace_sessions_user_id", table_name="vscode_workspace_sessions")
    op.drop_index("ix_vscode_workspace_sessions_org_id", table_name="vscode_workspace_sessions")
    op.drop_index("ix_vscode_workspace_sessions_project_id", table_name="vscode_workspace_sessions")
    op.drop_table("vscode_workspace_sessions")
    op.drop_index("ix_vscode_token_exchanges_user_id", table_name="vscode_token_exchanges")
    op.drop_index("ix_vscode_token_exchanges_org_id", table_name="vscode_token_exchanges")
    op.drop_index("ix_vscode_token_exchanges_session_token", table_name="vscode_token_exchanges")
    op.drop_index("ix_vscode_token_exchanges_exchange_token", table_name="vscode_token_exchanges")
    op.drop_table("vscode_token_exchanges")
    op.drop_index("ix_plugin_egress_decisions_org_id", table_name="plugin_egress_decisions")
    op.drop_index("ix_plugin_egress_decisions_plugin_id", table_name="plugin_egress_decisions")
    op.drop_table("plugin_egress_decisions")
    op.drop_index("ix_plugin_egress_policies_org_id", table_name="plugin_egress_policies")
    op.drop_index("ix_plugin_egress_policies_plugin_id", table_name="plugin_egress_policies")
    op.drop_table("plugin_egress_policies")
    for column in ("user_id", "project_id", "org_id", "installation_id", "plugin_id"):
        op.drop_index(f"ix_plugin_executions_{column}", table_name="plugin_executions")
    op.drop_table("plugin_executions")
    op.drop_index("ix_plugin_installations_project_id", table_name="plugin_installations")
    op.drop_index("ix_plugin_installations_org_id", table_name="plugin_installations")
    op.drop_index("ix_plugin_installations_plugin_id", table_name="plugin_installations")
    op.drop_table("plugin_installations")
    op.drop_index("ix_plugin_capabilities_plugin_version_id", table_name="plugin_capabilities")
    op.drop_table("plugin_capabilities")
    op.drop_index("ix_plugin_versions_plugin_id", table_name="plugin_versions")
    op.drop_table("plugin_versions")
    op.drop_index("ix_plugins_key", table_name="plugins")
    op.drop_table("plugins")
