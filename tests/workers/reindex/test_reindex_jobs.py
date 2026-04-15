from saturn.documents.db_models import DocumentParseJob
from saturn.documents.service import DocumentService
from saturn.storage.filesystem import FilesystemStorage
from saturn.workers.jobs.reindex import run_reindex_request
from tests.workers.parse.test_parse_jobs import _seed_project


def test_reindex_orchestrator_queues_parse_without_running_it(phase2_session_factory, tmp_path) -> None:
    session = phase2_session_factory()
    try:
        context, project_id = _seed_project(session)
        service = DocumentService(session, storage=FilesystemStorage(tmp_path))
        document = service.register_document(context, project_id, "Queued")
        session.flush()
        service.register_source_upload(
            context,
            document.id,
            "queued.md",
            "text/markdown",
            b"# Queued\n\nBody",
        )
        request = service.request_reindex(context, document.id, "test")
        session.flush()

        job = run_reindex_request(session, request.id)
        session.flush()

        assert request.status == "queued_parse"
        assert request.queued_parse_job_id == job.id
        assert job.status == "queued"
        assert session.query(DocumentParseJob).filter_by(status="succeeded").count() == 0
    finally:
        session.close()
