"""Pipeline routes."""

from fastapi import APIRouter

from saturn.api.deps import AuthContextDep, DbSessionDep
from saturn.pipeline.api_models import (
    HandoffPacketRead,
    PipelineApprovalCreate,
    PipelineDecisionCreate,
    PipelineRead,
    PipelineRejectCreate,
)
from saturn.pipeline.service import PipelineService

router = APIRouter(prefix="/api/v1/pipeline", tags=["pipeline"])


@router.get("/projects/{project_id}", response_model=PipelineRead)
async def get_pipeline(
    project_id: str, context: AuthContextDep, session: DbSessionDep
) -> PipelineRead:
    pipeline = PipelineService(session).get_for_project(context, project_id)
    if pipeline is None:
        raise LookupError("Pipeline not found")
    return PipelineRead.model_validate(pipeline)


@router.post("/projects/{project_id}/decisions", status_code=201)
async def add_decision(
    project_id: str,
    payload: PipelineDecisionCreate,
    context: AuthContextDep,
    session: DbSessionDep,
) -> dict[str, str]:
    decision = PipelineService(session).add_decision(
        context, project_id, payload.decision, payload.rationale
    )
    session.commit()
    return {"id": decision.id}


@router.post("/projects/{project_id}/approve", status_code=201)
async def approve(
    project_id: str,
    payload: PipelineApprovalCreate,
    context: AuthContextDep,
    session: DbSessionDep,
) -> dict[str, str]:
    approval = PipelineService(session).approve(context, project_id, payload.note)
    session.commit()
    return {"id": approval.id}


@router.post("/projects/{project_id}/reject", status_code=201)
async def reject(
    project_id: str,
    payload: PipelineRejectCreate,
    context: AuthContextDep,
    session: DbSessionDep,
) -> dict[str, str]:
    approval = PipelineService(session).reject(context, project_id, payload.note)
    session.commit()
    return {"id": approval.id}


@router.post("/projects/{project_id}/advance", response_model=PipelineRead)
async def advance(
    project_id: str,
    payload: PipelineApprovalCreate,
    context: AuthContextDep,
    session: DbSessionDep,
) -> PipelineRead:
    pipeline = PipelineService(session).advance(context, project_id, payload.override)
    session.commit()
    return PipelineRead.model_validate(pipeline)


@router.get("/projects/{project_id}/handoff", response_model=HandoffPacketRead)
async def handoff(
    project_id: str, context: AuthContextDep, session: DbSessionDep
) -> HandoffPacketRead:
    return HandoffPacketRead.model_validate(PipelineService(session).handoff_packet(context, project_id))
