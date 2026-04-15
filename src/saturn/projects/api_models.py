"""API models for projects."""

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str | None = Field(default=None, min_length=1, max_length=120)


class ProjectRead(BaseModel):
    id: str
    org_id: str
    name: str
    slug: str
    status: str

    model_config = {"from_attributes": True}


class ProjectMemberAdd(BaseModel):
    user_id: str
    role: str = Field(default="member", pattern="^(owner|admin|member|viewer)$")


class ProjectMemberRead(BaseModel):
    id: str
    project_id: str
    user_id: str
    role: str

    model_config = {"from_attributes": True}
