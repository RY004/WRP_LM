"""API-mediated pipeline plugin domain."""

from sqlalchemy.orm import Session

from saturn.access.context import AuthContext
from saturn.pipeline.service import PipelineService


class PipelinePluginDomain:
    def __init__(self, session: Session) -> None:
        self.service = PipelineService(session)

    def dispatch(self, context: AuthContext, project_id: str, action: str, payload: dict) -> dict:
        if action == "get":
            pipeline = self.service.get_for_project(context, project_id)
            if pipeline is None:
                raise LookupError("Pipeline not found")
            return {
                "id": pipeline.id,
                "project_id": pipeline.project_id,
                "current_stage": pipeline.current_stage,
                "cycle": pipeline.cycle,
                "status": pipeline.status,
            }
        if action == "handoff":
            return self.service.handoff_packet(context, project_id)
        if action == "add_decision":
            row = self.service.add_decision(
                context, project_id, payload.get("decision", ""), payload.get("rationale")
            )
            return {"id": row.id}
        if action == "advance":
            pipeline = self.service.advance(context, project_id, bool(payload.get("override", False)))
            return {"id": pipeline.id, "current_stage": pipeline.current_stage, "status": pipeline.status}
        raise ValueError(f"Unsupported pipeline action: {action}")
