"""Service layer for pipeline state."""

from sqlalchemy.orm import Session

from saturn.access.context import AuthContext
from saturn.access.policies import Permission
from saturn.access.service import AccessService
from saturn.pipeline.handoff import build_handoff_packet
from saturn.pipeline.repository import PipelineRepository
from saturn.pipeline.rules import can_advance, next_stage


class PipelineService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = PipelineRepository(session)
        self.access = AccessService(session)

    def get_for_project(self, context: AuthContext, project_id: str):
        self.access.require_project_permission(context, project_id, Permission.PIPELINE_READ)
        return self.repository.get_by_project(project_id)

    def add_decision(
        self, context: AuthContext, project_id: str, decision: str, rationale: str | None = None
    ):
        self.access.require_project_permission(context, project_id, Permission.PIPELINE_ADVANCE)
        pipeline = self._require_pipeline(project_id)
        row = self.repository.add_decision(pipeline, decision, rationale, context.user_id or "")
        self.session.flush()
        return row

    def approve(self, context: AuthContext, project_id: str, note: str | None = None):
        self.access.require_project_permission(context, project_id, Permission.PIPELINE_APPROVE)
        pipeline = self._require_pipeline(project_id)
        pipeline.status = "approved"
        row = self.repository.add_approval(pipeline, "approved", note, False, context.user_id or "")
        self.session.flush()
        return row

    def reject(self, context: AuthContext, project_id: str, note: str):
        self.access.require_project_permission(context, project_id, Permission.PIPELINE_APPROVE)
        pipeline = self._require_pipeline(project_id)
        pipeline.status = "rejected"
        row = self.repository.add_approval(pipeline, "rejected", note, False, context.user_id or "")
        self.session.flush()
        return row

    def advance(self, context: AuthContext, project_id: str, override: bool = False):
        self.access.require_project_permission(context, project_id, Permission.PIPELINE_ADVANCE)
        pipeline = self._require_pipeline(project_id)
        if not can_advance(pipeline.status, override=override):
            raise ValueError("Pipeline is not advanceable without override")
        following = next_stage(pipeline.current_stage)
        if following is None:
            pipeline.status = "complete"
        else:
            pipeline.current_stage = following
            pipeline.status = "active"
            if following == "question":
                pipeline.cycle += 1
        if override:
            self.repository.add_approval(
                pipeline, "override_advance", "Override advancement", True, context.user_id or ""
            )
        self.session.flush()
        return pipeline

    def handoff_packet(self, context: AuthContext, project_id: str) -> dict[str, object]:
        self.access.require_project_permission(context, project_id, Permission.PIPELINE_READ)
        return build_handoff_packet(self._require_pipeline(project_id))

    def _require_pipeline(self, project_id: str):
        pipeline = self.repository.get_by_project(project_id)
        if pipeline is None:
            raise LookupError("Pipeline not found")
        return pipeline
