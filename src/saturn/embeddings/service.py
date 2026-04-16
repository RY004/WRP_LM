"""Service layer for embeddings."""

import hashlib
from dataclasses import dataclass

from sqlalchemy.orm import Session

from saturn.access.context import AuthContext
from saturn.access.policies import Permission
from saturn.access.service import AccessService
from saturn.artifacts.db_models import Artifact
from saturn.documents.db_models import Document, DocumentChunk, DocumentVersion
from saturn.embeddings.batching import batch_texts
from saturn.embeddings.backends.base import EmbeddingBackend, EmbeddingVector
from saturn.embeddings.db_models import EmbeddingJob, EmbeddingRecord
from saturn.embeddings.model_registry import default_embedding_backend
from saturn.embeddings.repository import EmbeddingRepository


@dataclass(frozen=True, slots=True)
class EmbeddingSource:
    source_type: str
    source_id: str
    source_version_id: str | None
    project_id: str
    text: str


class EmbeddingService:
    def __init__(self, session: Session, backend: EmbeddingBackend | None = None) -> None:
        self.session = session
        self.backend = backend or default_embedding_backend()
        self.repository = EmbeddingRepository(session)
        self.access = AccessService(session)

    def embed_query(self, text: str) -> EmbeddingVector:
        return self.backend.embed([text])[0]

    def create_embed_job(
        self, context: AuthContext, project_id: str, source_type: str = "all", source_version_id: str | None = None
    ) -> EmbeddingJob:
        self.access.require_project_permission(context, project_id, Permission.PROJECT_WRITE)
        return self.repository.add(
            EmbeddingJob(
                project_id=project_id,
                source_type=source_type,
                source_version_id=source_version_id,
                queue_name="embed",
                status="queued",
            )
        )

    def embed_project(self, project_id: str, source_type: str = "all") -> list[EmbeddingRecord]:
        sources = self.collect_sources(project_id, source_type=source_type)
        records: list[EmbeddingRecord] = []
        for group in batch_texts([source.text for source in sources], batch_size=32):
            vectors = self.backend.embed(group)
            offset = len(records)
            for source, vector in zip(sources[offset : offset + len(group)], vectors, strict=True):
                records.append(self._store_source_embedding(source, vector))
        return records

    def collect_sources(self, project_id: str, source_type: str = "all") -> list[EmbeddingSource]:
        sources: list[EmbeddingSource] = []
        if source_type in {"all", "document_chunk"}:
            rows = (
                self.session.query(DocumentChunk, DocumentVersion, Document)
                .join(DocumentVersion, DocumentChunk.document_version_id == DocumentVersion.id)
                .join(Document, DocumentVersion.document_id == Document.id)
                .filter(Document.project_id == project_id)
                .all()
            )
            for chunk, version, document in rows:
                sources.append(
                    EmbeddingSource(
                        source_type="document_chunk",
                        source_id=chunk.id,
                        source_version_id=version.id,
                        project_id=document.project_id,
                        text=f"{chunk.heading_path_text}\n{chunk.text}",
                    )
                )
        if source_type in {"all", "artifact"}:
            for artifact in self.session.query(Artifact).filter(Artifact.project_id == project_id).all():
                text = artifact.index_projection.get("text") or artifact.rendered_markdown
                sources.append(
                    EmbeddingSource(
                        source_type="artifact",
                        source_id=artifact.id,
                        source_version_id=artifact.current_version_id,
                        project_id=artifact.project_id,
                        text=text,
                    )
                )
        return sources

    def _store_source_embedding(self, source: EmbeddingSource, vector: EmbeddingVector) -> EmbeddingRecord:
        return self.repository.upsert_record(
            project_id=source.project_id,
            source_type=source.source_type,
            source_id=source.source_id,
            source_version_id=source.source_version_id,
            model_name=vector.model_name,
            dimensions=vector.dimensions,
            vector=vector.values,
            text_hash=hashlib.sha256(source.text.encode("utf-8")).hexdigest(),
        )
