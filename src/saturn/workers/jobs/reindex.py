"""Reindex orchestration job implementation."""

from sqlalchemy.orm import Session

from saturn.documents.db_models import DocumentParseJob
from saturn.documents.repository import DocumentRepository
from saturn.documents.service import DocumentService


def run_reindex_request(session: Session, reindex_request_id: str) -> DocumentParseJob:
    repository = DocumentRepository(session)
    request = repository.get_reindex_request(reindex_request_id)
    if request is None:
        raise LookupError("Reindex request not found")
    request.status = "running"
    job = DocumentService(session).create_parse_job_for_current_version(request.document_id)
    session.flush()
    request.queued_parse_job_id = job.id
    request.status = "queued_parse"
    return job
