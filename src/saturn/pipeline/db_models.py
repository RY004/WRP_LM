"""Database models for pipeline state."""

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from saturn.db.base import Base
from saturn.shared.ids import new_id
from saturn.shared.time import utc_now


class PipelineState(Base):
    __tablename__ = "pipeline_states"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), unique=True, index=True
    )
    current_stage: Mapped[str] = mapped_column(String(64), nullable=False, default="question")
    cycle: Mapped[int] = mapped_column(default=1)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    branch_name: Mapped[str] = mapped_column(String(120), nullable=False, default="main")
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )

    project: Mapped["Project"] = relationship(back_populates="pipeline")


class PipelineDecision(Base):
    __tablename__ = "pipeline_decisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    pipeline_id: Mapped[str] = mapped_column(ForeignKey("pipeline_states.id", ondelete="CASCADE"))
    stage: Mapped[str] = mapped_column(String(64), nullable=False)
    cycle: Mapped[int] = mapped_column(default=1)
    decision: Mapped[str] = mapped_column(Text, nullable=False)
    rationale: Mapped[str | None] = mapped_column(Text)
    created_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=utc_now)


class PipelineApproval(Base):
    __tablename__ = "pipeline_approvals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    pipeline_id: Mapped[str] = mapped_column(ForeignKey("pipeline_states.id", ondelete="CASCADE"))
    stage: Mapped[str] = mapped_column(String(64), nullable=False)
    action: Mapped[str] = mapped_column(String(32), nullable=False)
    note: Mapped[str | None] = mapped_column(Text)
    override: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=utc_now)
