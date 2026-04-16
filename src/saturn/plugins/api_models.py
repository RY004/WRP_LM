"""API models for plugins, egress, and VS Code bridge flows."""

from typing import Any

from pydantic import BaseModel, Field


class PluginCapabilityDecl(BaseModel):
    capability: str
    domain: str = Field(pattern="^(pipeline|rag|wiki|egress)$")
    permissions: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class PluginRegisterRequest(BaseModel):
    key: str = Field(min_length=2, max_length=120)
    name: str
    description: str | None = None
    version: str = "1.0.0"
    entrypoint: str = "internal"
    manifest: dict[str, Any] = Field(default_factory=dict)
    capabilities: list[PluginCapabilityDecl] = Field(default_factory=list)


class PluginRead(BaseModel):
    id: str
    key: str
    name: str
    description: str | None
    status: str

    model_config = {"from_attributes": True}


class PluginVersionRead(BaseModel):
    id: str
    plugin_id: str
    version: str
    entrypoint: str
    manifest: dict[str, Any]
    status: str

    model_config = {"from_attributes": True}


class PluginInstallRequest(BaseModel):
    plugin_key: str
    version: str
    project_id: str | None = None
    enabled: bool = True


class PluginInstallationRead(BaseModel):
    id: str
    plugin_id: str
    plugin_version_id: str
    org_id: str
    project_id: str | None
    enabled: bool

    model_config = {"from_attributes": True}


class PluginEnableRequest(BaseModel):
    enabled: bool = True


class PluginExecuteRequest(BaseModel):
    plugin_key: str
    project_id: str
    capability: str
    input: dict[str, Any] = Field(default_factory=dict)


class PluginExecuteResponse(BaseModel):
    execution_id: str
    status: str
    result: dict[str, Any]


class EgressPolicyCreate(BaseModel):
    plugin_key: str
    project_id: str | None = None
    scheme: str = "https"
    host: str
    methods: list[str] = Field(default_factory=lambda: ["GET"])


class VSCodeTokenExchangeRequest(BaseModel):
    session_token: str


class VSCodeTokenExchangeResponse(BaseModel):
    exchange_token: str
    status: str


class VSCodeWorkspaceSessionRequest(BaseModel):
    exchange_token: str
    project_id: str
    workspace_uri: str
    agent_id: str | None = None


class VSCodeWorkspaceSessionRead(BaseModel):
    id: str
    project_id: str
    org_id: str
    user_id: str
    workspace_uri: str
    agent_id: str | None
    capabilities: list[str]
    status: str

    model_config = {"from_attributes": True}
