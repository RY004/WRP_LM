"""Documents and retrieval schema."""

from alembic import op
import sqlalchemy as sa

revision = "0005_documents_retrieval"
down_revision = "0004_artifacts_collaboration"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("project_id", sa.String(length=36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("source_kind", sa.String(length=64), nullable=False, server_default="upload"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="registered"),
        sa.Column("current_version_id", sa.String(length=36), nullable=True),
        sa.Column("current_version_number", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_by_user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("updated_by_user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_documents_project_id", "documents", ["project_id"])
    op.create_table(
        "document_sources",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("document_id", sa.String(length=36), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("storage_uri", sa.Text(), nullable=False),
        sa.Column("storage_key", sa.Text(), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("media_type", sa.String(length=160), nullable=False, server_default="application/octet-stream"),
        sa.Column("size_bytes", sa.Integer(), nullable=True),
        sa.Column("checksum", sa.String(length=128), nullable=True),
        sa.Column("created_by_user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_document_sources_document_id", "document_sources", ["document_id"])
    op.create_table(
        "document_versions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("document_id", sa.String(length=36), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_id", sa.String(length=36), sa.ForeignKey("document_sources.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("parse_status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("parser_name", sa.String(length=120), nullable=True),
        sa.Column("normalized_tree", sa.JSON(), nullable=False),
        sa.Column("rendered_markdown", sa.Text(), nullable=False, server_default=""),
        sa.Column("diagnostics_summary", sa.JSON(), nullable=False),
        sa.Column("created_by_user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("parsed_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("document_id", "version_number", name="uq_document_versions_number"),
    )
    op.create_index("ix_document_versions_document_id", "document_versions", ["document_id"])
    op.create_index("ix_document_versions_source_id", "document_versions", ["source_id"])
    op.create_table(
        "document_sections",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("document_version_id", sa.String(length=36), sa.ForeignKey("document_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("parent_section_id", sa.String(length=36), nullable=True),
        sa.Column("ordinal", sa.Integer(), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False, server_default=""),
        sa.Column("heading_path_text", sa.Text(), nullable=False),
        sa.Column("heading_path_ltree", sa.Text(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
    )
    op.create_index("ix_document_sections_document_version_id", "document_sections", ["document_version_id"])
    op.create_index("ix_document_sections_parent_section_id", "document_sections", ["parent_section_id"])
    op.create_table(
        "document_chunks",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("document_version_id", sa.String(length=36), sa.ForeignKey("document_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("section_id", sa.String(length=36), nullable=True),
        sa.Column("ordinal", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("heading_path_text", sa.Text(), nullable=False),
        sa.Column("heading_path_ltree", sa.Text(), nullable=False),
        sa.Column("token_count_estimate", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
    )
    op.create_index("ix_document_chunks_document_version_id", "document_chunks", ["document_version_id"])
    op.create_index("ix_document_chunks_section_id", "document_chunks", ["section_id"])
    op.create_table(
        "document_parse_diagnostics",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("document_version_id", sa.String(length=36), sa.ForeignKey("document_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False, server_default="info"),
        sa.Column("code", sa.String(length=120), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_document_parse_diagnostics_document_version_id", "document_parse_diagnostics", ["document_version_id"])
    op.create_table(
        "document_parse_jobs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("document_version_id", sa.String(length=36), sa.ForeignKey("document_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("queue_name", sa.String(length=64), nullable=False, server_default="parse"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="queued"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_document_parse_jobs_document_version_id", "document_parse_jobs", ["document_version_id"])
    op.create_table(
        "document_reindex_requests",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("document_id", sa.String(length=36), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("requested_by_user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="queued"),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("queued_parse_job_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_document_reindex_requests_document_id", "document_reindex_requests", ["document_id"])


def downgrade() -> None:
    op.drop_index("ix_document_reindex_requests_document_id", table_name="document_reindex_requests")
    op.drop_table("document_reindex_requests")
    op.drop_index("ix_document_parse_jobs_document_version_id", table_name="document_parse_jobs")
    op.drop_table("document_parse_jobs")
    op.drop_index(
        "ix_document_parse_diagnostics_document_version_id",
        table_name="document_parse_diagnostics",
    )
    op.drop_table("document_parse_diagnostics")
    op.drop_index("ix_document_chunks_section_id", table_name="document_chunks")
    op.drop_index("ix_document_chunks_document_version_id", table_name="document_chunks")
    op.drop_table("document_chunks")
    op.drop_index("ix_document_sections_parent_section_id", table_name="document_sections")
    op.drop_index("ix_document_sections_document_version_id", table_name="document_sections")
    op.drop_table("document_sections")
    op.drop_index("ix_document_versions_source_id", table_name="document_versions")
    op.drop_index("ix_document_versions_document_id", table_name="document_versions")
    op.drop_table("document_versions")
    op.drop_index("ix_document_sources_document_id", table_name="document_sources")
    op.drop_table("document_sources")
    op.drop_index("ix_documents_project_id", table_name="documents")
    op.drop_table("documents")
