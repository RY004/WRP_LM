"""API models for collaboration."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    body: str = Field(min_length=1)
    version_id: str | None = None


class CommentUpdate(BaseModel):
    body: str = Field(min_length=1)


class ArtifactCommentRead(BaseModel):
    id: str
    artifact_id: str
    version_id: str | None
    body: str
    status: str
    created_by_user_id: str

    model_config = {"from_attributes": True}


class StageCommentRead(BaseModel):
    id: str
    project_id: str
    stage: str
    body: str
    status: str
    created_by_user_id: str

    model_config = {"from_attributes": True}


class PhaseLockCreate(BaseModel):
    artifact_id: str | None = None
    ttl_seconds: int = Field(default=900, ge=30, le=3600)


class PhaseLockRead(BaseModel):
    id: str
    project_id: str
    stage: str
    holder_user_id: str
    artifact_id: str | None
    token: str
    expires_at: datetime

    model_config = {"from_attributes": True}


class PresenceUpsert(BaseModel):
    artifact_id: str | None = None
    cursor: dict[str, Any] | None = None
    ttl_seconds: int = Field(default=120, ge=30, le=600)


class PresenceRead(BaseModel):
    id: str
    project_id: str
    stage: str
    user_id: str
    artifact_id: str | None
    cursor: dict[str, Any] | None
    expires_at: datetime

    model_config = {"from_attributes": True}
