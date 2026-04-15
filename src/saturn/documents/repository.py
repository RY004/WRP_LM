"""Repository layer for documents."""

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from saturn.documents.db_models import (
    Document,
    DocumentChunk,
    DocumentParseJob,
    DocumentReindexRequest,
    DocumentSection,
    DocumentSource,
    DocumentVersion,
    ParseDiagnostic,
)


class DocumentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, model):
        self.session.add(model)
        return model

    def get_document(self, document_id: str) -> Document | None:
        return self.session.get(Document, document_id)

    def list_documents(self, project_id: str) -> list[Document]:
        return list(
            self.session.scalars(
                select(Document).where(Document.project_id == project_id).order_by(Document.updated_at.desc())
            )
        )

    def get_version(self, version_id: str) -> DocumentVersion | None:
        return self.session.get(DocumentVersion, version_id)

    def list_versions(self, document_id: str) -> list[DocumentVersion]:
        return list(
            self.session.scalars(
                select(DocumentVersion)
                .where(DocumentVersion.document_id == document_id)
                .order_by(DocumentVersion.version_number)
            )
        )

    def get_source(self, source_id: str) -> DocumentSource | None:
        return self.session.get(DocumentSource, source_id)

    def get_parse_job(self, job_id: str) -> DocumentParseJob | None:
        return self.session.get(DocumentParseJob, job_id)

    def list_parse_jobs_for_version(self, version_id: str) -> list[DocumentParseJob]:
        return list(
            self.session.scalars(
                select(DocumentParseJob)
                .where(DocumentParseJob.document_version_id == version_id)
                .order_by(DocumentParseJob.created_at)
            )
        )

    def latest_parse_job_for_version(self, version_id: str) -> DocumentParseJob | None:
        return self.session.scalar(
            select(DocumentParseJob)
            .where(DocumentParseJob.document_version_id == version_id)
            .order_by(DocumentParseJob.created_at.desc())
            .limit(1)
        )

    def get_reindex_request(self, request_id: str) -> DocumentReindexRequest | None:
        return self.session.get(DocumentReindexRequest, request_id)

    def replace_parse_rows(
        self,
        version_id: str,
        sections: list[DocumentSection],
        chunks: list[DocumentChunk],
        diagnostics: list[ParseDiagnostic],
    ) -> None:
        self.session.execute(delete(DocumentChunk).where(DocumentChunk.document_version_id == version_id))
        self.session.execute(delete(DocumentSection).where(DocumentSection.document_version_id == version_id))
        self.session.execute(delete(ParseDiagnostic).where(ParseDiagnostic.document_version_id == version_id))
        self.session.add_all(sections)
        self.session.flush()
        self.session.add_all(chunks)
        self.session.add_all(diagnostics)
