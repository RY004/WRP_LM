"""Embed worker job implementation."""

from sqlalchemy.orm import Session

from saturn.embeddings.repository import EmbeddingRepository
from saturn.embeddings.service import EmbeddingService


def run_embed_job(session: Session, embed_job_id: str):
    repository = EmbeddingRepository(session)
    job = repository.get_job(embed_job_id)
    if job is None:
        raise LookupError("Embedding job not found")
    job.status = "running"
    job.attempts += 1
    try:
        records = EmbeddingService(session).embed_project(job.project_id, source_type=job.source_type)
    except Exception as exc:
        job.status = "failed"
        job.last_error = str(exc)
        return []
    job.status = "succeeded"
    job.last_error = None
    return records
