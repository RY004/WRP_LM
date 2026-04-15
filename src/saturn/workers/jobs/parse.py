"""Parse worker job implementation."""

from sqlalchemy.orm import Session

from saturn.documents.db_models import DocumentParseJob
from saturn.documents.repository import DocumentRepository
from saturn.documents.service import DocumentService
from saturn.storage.base import StorageBackend


def run_parse_job(session: Session, storage: StorageBackend, parse_job_id: str) -> DocumentParseJob:
    repository = DocumentRepository(session)
    job = repository.get_parse_job(parse_job_id)
    if job is None:
        raise LookupError("Parse job not found")
    job.status = "running"
    job.attempts += 1
    try:
        DocumentService(session, storage=storage).parse_version(job.document_version_id)
    except Exception as exc:
        job.status = "failed"
        job.last_error = str(exc)
        DocumentService(session, storage=storage).mark_parse_failed(job.document_version_id, str(exc))
    else:
        job.status = "succeeded"
        job.last_error = None
    return job


def parse_version(session: Session, storage: StorageBackend, document_version_id: str):
    """Convenience entrypoint used by tests and local jobs."""
    return DocumentService(session, storage=storage).parse_version(document_version_id)
