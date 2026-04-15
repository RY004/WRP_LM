"""Projects and pipeline migration scaffold."""

from alembic import op
import sqlalchemy as sa

revision = "0003_projects_pipeline"
down_revision = "0002_identity_access"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("org_id", sa.String(length=36), sa.ForeignKey("organizations.id", ondelete="CASCADE")),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("created_by_user_id", sa.String(length=36), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_projects_slug", "projects", ["slug"])
    op.create_table(
        "project_memberships",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("project_id", sa.String(length=36), sa.ForeignKey("projects.id", ondelete="CASCADE")),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("role", sa.String(length=32), nullable=False, server_default="member"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("project_id", "user_id", name="uq_project_memberships_project_user"),
    )
    op.create_table(
        "acl_grants",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("project_id", sa.String(length=36), sa.ForeignKey("projects.id", ondelete="CASCADE")),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("permission", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("project_id", "user_id", "permission", name="uq_acl_grants"),
    )
    op.create_table(
        "pipeline_states",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("project_id", sa.String(length=36), sa.ForeignKey("projects.id", ondelete="CASCADE")),
        sa.Column("current_stage", sa.String(length=64), nullable=False, server_default="question"),
        sa.Column("cycle", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("branch_name", sa.String(length=120), nullable=False, server_default="main"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("project_id", name="uq_pipeline_states_project_id"),
    )
    op.create_index("ix_pipeline_states_project_id", "pipeline_states", ["project_id"])
    op.create_table(
        "pipeline_decisions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("pipeline_id", sa.String(length=36), sa.ForeignKey("pipeline_states.id", ondelete="CASCADE")),
        sa.Column("stage", sa.String(length=64), nullable=False),
        sa.Column("cycle", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("decision", sa.Text(), nullable=False),
        sa.Column("rationale", sa.Text()),
        sa.Column("created_by_user_id", sa.String(length=36), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "pipeline_approvals",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("pipeline_id", sa.String(length=36), sa.ForeignKey("pipeline_states.id", ondelete="CASCADE")),
        sa.Column("stage", sa.String(length=64), nullable=False),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column("note", sa.Text()),
        sa.Column("override", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_by_user_id", sa.String(length=36), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("pipeline_approvals")
    op.drop_table("pipeline_decisions")
    op.drop_index("ix_pipeline_states_project_id", table_name="pipeline_states")
    op.drop_table("pipeline_states")
    op.drop_table("acl_grants")
    op.drop_table("project_memberships")
    op.drop_index("ix_projects_slug", table_name="projects")
    op.drop_table("projects")
