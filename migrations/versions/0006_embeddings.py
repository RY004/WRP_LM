"""Embeddings schema."""

from alembic import op
import sqlalchemy as sa

revision = "0006_embeddings"
down_revision = "0005_documents_retrieval"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "embedding_records",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("project_id", sa.String(length=36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("source_id", sa.String(length=36), nullable=False),
        sa.Column("source_version_id", sa.String(length=36), nullable=True),
        sa.Column("model_name", sa.String(length=120), nullable=False),
        sa.Column("dimensions", sa.Integer(), nullable=False),
        sa.Column("vector", sa.JSON(), nullable=False),
        sa.Column("text_hash", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="ready"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("source_type", "source_id", "model_name", name="uq_embedding_records_source_model"),
    )
    op.create_index("ix_embedding_records_project_id", "embedding_records", ["project_id"])
    op.create_index("ix_embedding_records_source_type", "embedding_records", ["source_type"])
    op.create_index("ix_embedding_records_source_id", "embedding_records", ["source_id"])
    op.create_index("ix_embedding_records_source_version_id", "embedding_records", ["source_version_id"])
    op.create_table(
        "embedding_jobs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("project_id", sa.String(length=36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("source_version_id", sa.String(length=36), nullable=True),
        sa.Column("queue_name", sa.String(length=64), nullable=False, server_default="embed"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="queued"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_embedding_jobs_project_id", "embedding_jobs", ["project_id"])
    op.create_index("ix_embedding_jobs_source_version_id", "embedding_jobs", ["source_version_id"])


def downgrade() -> None:
    op.drop_index("ix_embedding_jobs_source_version_id", table_name="embedding_jobs")
    op.drop_index("ix_embedding_jobs_project_id", table_name="embedding_jobs")
    op.drop_table("embedding_jobs")
    op.drop_index("ix_embedding_records_source_version_id", table_name="embedding_records")
    op.drop_index("ix_embedding_records_source_id", table_name="embedding_records")
    op.drop_index("ix_embedding_records_source_type", table_name="embedding_records")
    op.drop_index("ix_embedding_records_project_id", table_name="embedding_records")
    op.drop_table("embedding_records")
