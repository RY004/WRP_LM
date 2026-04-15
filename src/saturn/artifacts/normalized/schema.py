"""Normalized artifact schema definitions."""

from typing import Any, Literal

from pydantic import BaseModel, Field


BlockType = Literal["heading", "paragraph", "list", "code"]


class NormalizedBlock(BaseModel):
    type: BlockType
    text: str | None = None
    level: int | None = Field(default=None, ge=1, le=6)
    items: list[str] | None = None
    language: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class NormalizedArtifact(BaseModel):
    schema_version: str = Field(default="saturn.normalized.v1")
    title: str = Field(min_length=1, max_length=255)
    blocks: list[NormalizedBlock] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
