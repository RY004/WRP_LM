"""API models for Notion integration."""

from pydantic import BaseModel, Field


class NotionOAuthStartRead(BaseModel):
    authorization_url: str
    state: str


class NotionOAuthCallback(BaseModel):
    code: str
    state: str


class NotionAccountRead(BaseModel):
    id: str
    org_id: str
    owner_user_id: str
    workspace_id: str
    workspace_name: str
    status: str
    reconnect_reason: str | None

    model_config = {"from_attributes": True}


class NotionResourceRead(BaseModel):
    id: str
    resource_type: str
    title: str
    updated_cursor: str | None = None


class NotionSyncTargetCreate(BaseModel):
    account_id: str
    project_id: str
    notion_resource_id: str
    resource_type: str = Field(pattern="^(page|database)$")
    title: str = Field(min_length=1, max_length=255)


class NotionSyncTargetRead(BaseModel):
    id: str
    account_id: str
    project_id: str
    notion_resource_id: str
    resource_type: str
    title: str
    status: str
    cursor: str | None
    document_id: str | None
    last_error: str | None

    model_config = {"from_attributes": True}


class NotionSyncJobRead(BaseModel):
    id: str
    target_id: str
    queue_name: str
    status: str
    attempts: int
    retry_after_seconds: int | None
    queued_parse_job_id: str | None
    queued_embed_job_id: str | None
    diagnostics: dict
    last_error: str | None

    model_config = {"from_attributes": True}
