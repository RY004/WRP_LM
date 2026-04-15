"""Repository layer for pipeline state."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from saturn.pipeline.db_models import PipelineApproval, PipelineDecision, PipelineState


class PipelineRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, project_id: str) -> PipelineState:
        pipeline = PipelineState(project_id=project_id)
        self.session.add(pipeline)
        return pipeline

    def get(self, pipeline_id: str) -> PipelineState | None:
        return self.session.get(PipelineState, pipeline_id)

    def get_by_project(self, project_id: str) -> PipelineState | None:
        return self.session.scalar(select(PipelineState).where(PipelineState.project_id == project_id))

    def add_decision(
        self,
        pipeline: PipelineState,
        decision: str,
        rationale: str | None,
        user_id: str,
    ) -> PipelineDecision:
        row = PipelineDecision(
            pipeline_id=pipeline.id,
            stage=pipeline.current_stage,
            cycle=pipeline.cycle,
            decision=decision,
            rationale=rationale,
            created_by_user_id=user_id,
        )
        self.session.add(row)
        return row

    def add_approval(
        self,
        pipeline: PipelineState,
        action: str,
        note: str | None,
        override: bool,
        user_id: str,
    ) -> PipelineApproval:
        row = PipelineApproval(
            pipeline_id=pipeline.id,
            stage=pipeline.current_stage,
            action=action,
            note=note,
            override=override,
            created_by_user_id=user_id,
        )
        self.session.add(row)
        return row
