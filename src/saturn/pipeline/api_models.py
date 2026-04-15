"""API models for pipeline state."""

from pydantic import BaseModel, Field


class PipelineRead(BaseModel):
    id: str
    project_id: str
    current_stage: str
    cycle: int
    status: str
    branch_name: str

    model_config = {"from_attributes": True}


class PipelineDecisionCreate(BaseModel):
    decision: str = Field(min_length=1)
    rationale: str | None = None


class PipelineApprovalCreate(BaseModel):
    note: str | None = None
    override: bool = False


class PipelineRejectCreate(BaseModel):
    note: str = Field(min_length=1)


class HandoffPacketRead(BaseModel):
    project_id: str
    pipeline_id: str
    stage: str
    cycle: int
    status: str
    next_stage: str | None
    branch_name: str
