"""API models for the identity domain."""

from pydantic import BaseModel, EmailStr, Field


class UserRead(BaseModel):
    id: str
    email: EmailStr
    display_name: str | None = None

    model_config = {"from_attributes": True}


class SessionRead(BaseModel):
    session_id: str
    user: UserRead
    org_id: str


class GoogleOAuthStartResponse(BaseModel):
    authorization_url: str
    state: str


class GoogleOAuthCallbackRequest(BaseModel):
    email: EmailStr
    name: str | None = None
    org_name: str = Field(default="Saturn Workspace", min_length=1, max_length=255)
    org_slug: str = Field(default="saturn-workspace", min_length=1, max_length=120)
