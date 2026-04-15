"""API models for artifacts."""

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


ArtifactStatus = Literal["draft", "review", "approved", "archived"]


class ArtifactCreate(BaseModel):
    project_id: str
    title: str = Field(min_length=1, max_length=255)
    slug: str | None = Field(default=None, min_length=1, max_length=160)
    artifact_type: str = Field(default="document", min_length=1, max_length=64)
    normalized_content: dict[str, Any] | None = None
    markdown: str | None = None
    stage: str | None = Field(default=None, max_length=64)
    lock_token: str | None = None

    @model_validator(mode="after")
    def require_content(self):
        if self.normalized_content is None and self.markdown is None:
            raise ValueError("normalized_content or markdown is required")
        return self


class ArtifactUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    status: ArtifactStatus | None = None
    normalized_content: dict[str, Any] | None = None
    markdown: str | None = None
    change_summary: str | None = None
    stage: str | None = Field(default=None, max_length=64)
    lock_token: str | None = None


class ArtifactVersionCreate(BaseModel):
    normalized_content: dict[str, Any] | None = None
    markdown: str | None = None
    change_summary: str | None = None
    stage: str | None = Field(default=None, max_length=64)
    lock_token: str | None = None


class ArtifactRead(BaseModel):
    id: str
    project_id: str
    slug: str
    title: str
    artifact_type: str
    status: str
    current_version_number: int
    normalized_content: dict[str, Any]
    rendered_markdown: str
    index_projection: dict[str, Any]

    model_config = {"from_attributes": True}


class ArtifactVersionRead(BaseModel):
    id: str
    artifact_id: str
    version_number: int
    normalized_content: dict[str, Any]
    rendered_markdown: str
    index_projection: dict[str, Any]
    change_summary: str | None

    model_config = {"from_attributes": True}


class ArtifactMergeRequest(BaseModel):
    base: dict[str, Any]
    left: dict[str, Any]
    right: dict[str, Any]
