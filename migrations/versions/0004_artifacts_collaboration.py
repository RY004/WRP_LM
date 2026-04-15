"""Artifacts and collaboration migration scaffold."""

from alembic import op
import sqlalchemy as sa

revision = "0004_artifacts_collaboration"
down_revision = "0003_projects_pipeline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "artifacts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("project_id", sa.String(length=36), sa.ForeignKey("projects.id", ondelete="CASCADE")),
        sa.Column("slug", sa.String(length=160), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("artifact_type", sa.String(length=64), nullable=False, server_default="document"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("current_version_id", sa.String(length=36)),
        sa.Column("current_version_number", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("normalized_content", sa.JSON(), nullable=False),
        sa.Column("rendered_markdown", sa.Text(), nullable=False),
        sa.Column("index_projection", sa.JSON(), nullable=False),
        sa.Column("created_by_user_id", sa.String(length=36), sa.ForeignKey("users.id")),
        sa.Column("updated_by_user_id", sa.String(length=36), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("project_id", "slug", name="uq_artifacts_project_slug"),
    )
    op.create_index("ix_artifacts_project_id", "artifacts", ["project_id"])
    op.create_table(
        "artifact_versions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("artifact_id", sa.String(length=36), sa.ForeignKey("artifacts.id", ondelete="CASCADE")),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("normalized_content", sa.JSON(), nullable=False),
        sa.Column("rendered_markdown", sa.Text(), nullable=False),
        sa.Column("index_projection", sa.JSON(), nullable=False),
        sa.Column("change_summary", sa.Text()),
        sa.Column("created_by_user_id", sa.String(length=36), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("artifact_id", "version_number", name="uq_artifact_versions_number"),
    )
    op.create_index("ix_artifact_versions_artifact_id", "artifact_versions", ["artifact_id"])
    op.create_table(
        "artifact_comments",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("artifact_id", sa.String(length=36), sa.ForeignKey("artifacts.id", ondelete="CASCADE")),
        sa.Column("version_id", sa.String(length=36), sa.ForeignKey("artifact_versions.id", ondelete="SET NULL")),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("created_by_user_id", sa.String(length=36), sa.ForeignKey("users.id")),
        sa.Column("updated_by_user_id", sa.String(length=36), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_artifact_comments_artifact_id", "artifact_comments", ["artifact_id"])
    op.create_table(
        "stage_comments",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("project_id", sa.String(length=36), sa.ForeignKey("projects.id", ondelete="CASCADE")),
        sa.Column("stage", sa.String(length=64), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("created_by_user_id", sa.String(length=36), sa.ForeignKey("users.id")),
        sa.Column("updated_by_user_id", sa.String(length=36), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_stage_comments_project_id", "stage_comments", ["project_id"])
    op.create_index("ix_stage_comments_stage", "stage_comments", ["stage"])
    op.create_table(
        "presence_markers",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("project_id", sa.String(length=36), sa.ForeignKey("projects.id", ondelete="CASCADE")),
        sa.Column("stage", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("artifact_id", sa.String(length=36), sa.ForeignKey("artifacts.id", ondelete="SET NULL")),
        sa.Column("cursor", sa.JSON()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("project_id", "stage", "user_id", name="uq_presence_project_stage_user"),
    )
    op.create_index("ix_presence_markers_project_id", "presence_markers", ["project_id"])
    op.create_index("ix_presence_markers_stage", "presence_markers", ["stage"])
    op.create_table(
        "phase_locks",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("project_id", sa.String(length=36), sa.ForeignKey("projects.id", ondelete="CASCADE")),
        sa.Column("stage", sa.String(length=64), nullable=False),
        sa.Column("holder_user_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("artifact_id", sa.String(length=36), sa.ForeignKey("artifacts.id", ondelete="SET NULL")),
        sa.Column("token", sa.String(length=80), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("project_id", "stage", name="uq_phase_locks_project_stage"),
        sa.UniqueConstraint("token", name="uq_phase_locks_token"),
    )
    op.create_index("ix_phase_locks_project_id", "phase_locks", ["project_id"])
    op.create_index("ix_phase_locks_stage", "phase_locks", ["stage"])


def downgrade() -> None:
    op.drop_index("ix_phase_locks_stage", table_name="phase_locks")
    op.drop_index("ix_phase_locks_project_id", table_name="phase_locks")
    op.drop_table("phase_locks")
    op.drop_index("ix_presence_markers_stage", table_name="presence_markers")
    op.drop_index("ix_presence_markers_project_id", table_name="presence_markers")
    op.drop_table("presence_markers")
    op.drop_index("ix_stage_comments_stage", table_name="stage_comments")
    op.drop_index("ix_stage_comments_project_id", table_name="stage_comments")
    op.drop_table("stage_comments")
    op.drop_index("ix_artifact_comments_artifact_id", table_name="artifact_comments")
    op.drop_table("artifact_comments")
    op.drop_index("ix_artifact_versions_artifact_id", table_name="artifact_versions")
    op.drop_table("artifact_versions")
    op.drop_index("ix_artifacts_project_id", table_name="artifacts")
    op.drop_table("artifacts")
