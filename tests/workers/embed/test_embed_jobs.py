from saturn.documents.db_models import DocumentChunk
from saturn.documents.service import DocumentService
from saturn.embeddings.db_models import EmbeddingRecord
from saturn.embeddings.service import EmbeddingService
from saturn.storage.filesystem import FilesystemStorage
from saturn.workers.jobs.embed import run_embed_job
from saturn.workers.jobs.parse import run_parse_job
from tests.workers.parse.test_parse_jobs import _seed_project


def test_embed_job_indexes_document_chunks(phase2_session_factory, tmp_path) -> None:
    session = phase2_session_factory()
    try:
        context, project_id = _seed_project(session)
        storage = FilesystemStorage(tmp_path)
        document_service = DocumentService(session, storage=storage)
        document = document_service.register_document(context, project_id, "Embedding Doc")
        session.flush()
        _, _version, parse_job = document_service.register_source_upload(
            context,
            document.id,
            "embedding.md",
            "text/markdown",
            b"# Embeddings\n\nVector retrieval text",
        )
        run_parse_job(session, storage, parse_job.id)
        embed_job = EmbeddingService(session).create_embed_job(context, project_id)
        session.flush()

        records = run_embed_job(session, embed_job.id)
        session.flush()

        chunk = session.query(DocumentChunk).one()
        record = session.query(EmbeddingRecord).filter_by(source_id=chunk.id).one()
        assert embed_job.status == "succeeded"
        assert records
        assert record.source_type == "document_chunk"
        assert record.dimensions == 64
        assert len(record.vector) == 64
    finally:
        session.close()
