"""Notion sync schema."""

from alembic import op
import sqlalchemy as sa

revision = "0007_notion_sync"
down_revision = "0006_embeddings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notion_oauth_states",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("state", sa.String(length=128), nullable=False),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("org_id", sa.String(length=36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("state", name="uq_notion_oauth_states_state"),
    )
    op.create_index("ix_notion_oauth_states_state", "notion_oauth_states", ["state"])
    op.create_index("ix_notion_oauth_states_user_id", "notion_oauth_states", ["user_id"])
    op.create_index("ix_notion_oauth_states_org_id", "notion_oauth_states", ["org_id"])
    op.create_table(
        "notion_accounts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("org_id", sa.String(length=36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("owner_user_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("workspace_id", sa.String(length=160), nullable=False),
        sa.Column("workspace_name", sa.String(length=255), nullable=False),
        sa.Column("bot_id", sa.String(length=160), nullable=True),
        sa.Column("access_token_encrypted", sa.Text(), nullable=False),
        sa.Column("refresh_token_encrypted", sa.Text(), nullable=True),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("reconnect_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("org_id", "workspace_id", name="uq_notion_accounts_org_workspace"),
    )
    op.create_index("ix_notion_accounts_org_id", "notion_accounts", ["org_id"])
    op.create_index("ix_notion_accounts_owner_user_id", "notion_accounts", ["owner_user_id"])
    op.create_table(
        "notion_sync_targets",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("account_id", sa.String(length=36), sa.ForeignKey("notion_accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("project_id", sa.String(length=36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("notion_resource_id", sa.String(length=160), nullable=False),
        sa.Column("resource_type", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("cursor", sa.Text(), nullable=True),
        sa.Column("document_id", sa.String(length=36), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_by_user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("project_id", "notion_resource_id", name="uq_notion_targets_project_resource"),
    )
    op.create_index("ix_notion_sync_targets_account_id", "notion_sync_targets", ["account_id"])
    op.create_index("ix_notion_sync_targets_project_id", "notion_sync_targets", ["project_id"])
    op.create_index("ix_notion_sync_targets_document_id", "notion_sync_targets", ["document_id"])
    op.create_table(
        "notion_sync_jobs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("target_id", sa.String(length=36), sa.ForeignKey("notion_sync_targets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("queue_name", sa.String(length=64), nullable=False, server_default="notion_sync"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="queued"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("retry_after_seconds", sa.Integer(), nullable=True),
        sa.Column("queued_parse_job_id", sa.String(length=36), nullable=True),
        sa.Column("queued_embed_job_id", sa.String(length=36), nullable=True),
        sa.Column("diagnostics", sa.JSON(), nullable=False),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_notion_sync_jobs_target_id", "notion_sync_jobs", ["target_id"])


def downgrade() -> None:
    op.drop_index("ix_notion_sync_jobs_target_id", table_name="notion_sync_jobs")
    op.drop_table("notion_sync_jobs")
    op.drop_index("ix_notion_sync_targets_document_id", table_name="notion_sync_targets")
    op.drop_index("ix_notion_sync_targets_project_id", table_name="notion_sync_targets")
    op.drop_index("ix_notion_sync_targets_account_id", table_name="notion_sync_targets")
    op.drop_table("notion_sync_targets")
    op.drop_index("ix_notion_accounts_owner_user_id", table_name="notion_accounts")
    op.drop_index("ix_notion_accounts_org_id", table_name="notion_accounts")
    op.drop_table("notion_accounts")
    op.drop_index("ix_notion_oauth_states_org_id", table_name="notion_oauth_states")
    op.drop_index("ix_notion_oauth_states_user_id", table_name="notion_oauth_states")
    op.drop_index("ix_notion_oauth_states_state", table_name="notion_oauth_states")
    op.drop_table("notion_oauth_states")
