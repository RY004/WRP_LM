"""Database models for document intake and parsed content."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from saturn.db.base import Base
from saturn.shared.ids import new_id
from saturn.shared.time import utc_now


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source_kind: Mapped[str] = mapped_column(String(64), nullable=False, default="upload")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="registered")
    current_version_id: Mapped[str | None] = mapped_column(String(36))
    current_version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    updated_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    versions: Mapped[list["DocumentVersion"]] = relationship(
        back_populates="document", cascade="all, delete-orphan", foreign_keys="DocumentVersion.document_id"
    )


class DocumentSource(Base):
    __tablename__ = "document_sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    storage_uri: Mapped[str] = mapped_column(Text, nullable=False)
    storage_key: Mapped[str] = mapped_column(Text, nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    media_type: Mapped[str] = mapped_column(String(160), nullable=False, default="application/octet-stream")
    size_bytes: Mapped[int | None] = mapped_column(Integer)
    checksum: Mapped[str | None] = mapped_column(String(128))
    created_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class DocumentVersion(Base):
    __tablename__ = "document_versions"
    __table_args__ = (UniqueConstraint("document_id", "version_number", name="uq_document_versions_number"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("document_sources.id", ondelete="CASCADE"), index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    parse_status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    parser_name: Mapped[str | None] = mapped_column(String(120))
    normalized_tree: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    rendered_markdown: Mapped[str] = mapped_column(Text, nullable=False, default="")
    diagnostics_summary: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    parsed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    document: Mapped[Document] = relationship(
        back_populates="versions", foreign_keys=[document_id]
    )


class DocumentSection(Base):
    __tablename__ = "document_sections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    document_version_id: Mapped[str] = mapped_column(
        ForeignKey("document_versions.id", ondelete="CASCADE"), index=True
    )
    parent_section_id: Mapped[str | None] = mapped_column(String(36), index=True)
    ordinal: Mapped[int] = mapped_column(Integer, nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False, default="")
    heading_path_text: Mapped[str] = mapped_column(Text, nullable=False)
    heading_path_ltree: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    document_version_id: Mapped[str] = mapped_column(
        ForeignKey("document_versions.id", ondelete="CASCADE"), index=True
    )
    section_id: Mapped[str | None] = mapped_column(String(36), index=True)
    ordinal: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    heading_path_text: Mapped[str] = mapped_column(Text, nullable=False)
    heading_path_ltree: Mapped[str] = mapped_column(Text, nullable=False)
    token_count_estimate: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)


class ParseDiagnostic(Base):
    __tablename__ = "document_parse_diagnostics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    document_version_id: Mapped[str] = mapped_column(
        ForeignKey("document_versions.id", ondelete="CASCADE"), index=True
    )
    severity: Mapped[str] = mapped_column(String(32), nullable=False, default="info")
    code: Mapped[str] = mapped_column(String(120), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class DocumentParseJob(Base):
    __tablename__ = "document_parse_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    document_version_id: Mapped[str] = mapped_column(
        ForeignKey("document_versions.id", ondelete="CASCADE"), index=True
    )
    queue_name: Mapped[str] = mapped_column(String(64), nullable=False, default="parse")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="queued")
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


class DocumentReindexRequest(Base):
    __tablename__ = "document_reindex_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    requested_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="queued")
    reason: Mapped[str | None] = mapped_column(Text)
    queued_parse_job_id: Mapped[str | None] = mapped_column(String(36))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
