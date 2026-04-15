"""Pipeline handoff packet helpers."""

from saturn.pipeline.db_models import PipelineState
from saturn.pipeline.rules import next_stage


def build_handoff_packet(pipeline: PipelineState) -> dict[str, object]:
    return {
        "project_id": pipeline.project_id,
        "pipeline_id": pipeline.id,
        "stage": pipeline.current_stage,
        "cycle": pipeline.cycle,
        "status": pipeline.status,
        "next_stage": next_stage(pipeline.current_stage),
        "branch_name": pipeline.branch_name,
    }
