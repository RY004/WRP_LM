"""Retrieval routes."""

from fastapi import APIRouter

from saturn.api.deps import AuthContextDep, DbSessionDep
from saturn.embeddings.service import EmbeddingService
from saturn.retrieval.api_models import RetrievalQuery, RetrievalResponse
from saturn.retrieval.service import RetrievalService

router = APIRouter(prefix="/api/v1/retrieval", tags=["retrieval"])


@router.post("/query", response_model=RetrievalResponse)
async def query_retrieval(
    payload: RetrievalQuery, context: AuthContextDep, session: DbSessionDep
) -> RetrievalResponse:
    return RetrievalService(session).query(
        context,
        project_id=payload.project_id,
        query=payload.query,
        mode=payload.mode,
        section_path_prefix=payload.section_path_prefix,
        include_documents=payload.include_documents,
        include_artifacts=payload.include_artifacts,
        limit=payload.limit,
    )


@router.post("/projects/{project_id}/embedding-jobs", status_code=202)
async def create_embedding_job(
    project_id: str,
    context: AuthContextDep,
    session: DbSessionDep,
    source_type: str = "all",
) -> dict:
    job = EmbeddingService(session).create_embed_job(context, project_id, source_type=source_type)
    session.commit()
    return {"id": job.id, "queue_name": job.queue_name, "status": job.status}
