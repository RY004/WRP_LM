"""Database models for Notion integration."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from saturn.db.base import Base
from saturn.shared.ids import new_id
from saturn.shared.time import utc_now


class NotionOAuthState(Base):
    __tablename__ = "notion_oauth_states"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    state: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class NotionAccount(Base):
    __tablename__ = "notion_accounts"
    __table_args__ = (
        UniqueConstraint("org_id", "workspace_id", name="uq_notion_accounts_org_workspace"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    owner_user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    workspace_id: Mapped[str] = mapped_column(String(160), nullable=False)
    workspace_name: Mapped[str] = mapped_column(String(255), nullable=False)
    bot_id: Mapped[str | None] = mapped_column(String(160))
    access_token_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token_encrypted: Mapped[str | None] = mapped_column(Text)
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    reconnect_reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


class NotionSyncTarget(Base):
    __tablename__ = "notion_sync_targets"
    __table_args__ = (
        UniqueConstraint("project_id", "notion_resource_id", name="uq_notion_targets_project_resource"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    account_id: Mapped[str] = mapped_column(ForeignKey("notion_accounts.id", ondelete="CASCADE"), index=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    notion_resource_id: Mapped[str] = mapped_column(String(160), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    cursor: Mapped[str | None] = mapped_column(Text)
    document_id: Mapped[str | None] = mapped_column(String(36), index=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[str | None] = mapped_column(Text)
    created_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


class NotionSyncJob(Base):
    __tablename__ = "notion_sync_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    target_id: Mapped[str] = mapped_column(ForeignKey("notion_sync_targets.id", ondelete="CASCADE"), index=True)
    queue_name: Mapped[str] = mapped_column(String(64), nullable=False, default="notion_sync")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="queued")
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    retry_after_seconds: Mapped[int | None] = mapped_column(Integer)
    queued_parse_job_id: Mapped[str | None] = mapped_column(String(36))
    queued_embed_job_id: Mapped[str | None] = mapped_column(String(36))
    diagnostics: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    last_error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
