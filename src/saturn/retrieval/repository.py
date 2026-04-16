"""Repository layer for retrieval."""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from saturn.artifacts.db_models import Artifact
from saturn.documents.db_models import Document, DocumentChunk, DocumentSection, DocumentVersion
from saturn.embeddings.repository import EmbeddingRepository


@dataclass(frozen=True, slots=True)
class RetrievalCandidate:
    source_type: str
    source_id: str
    project_id: str
    title: str
    text: str
    heading_path_text: str | None = None
    heading_path_ltree: str | None = None


class RetrievalRepository:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.embeddings = EmbeddingRepository(session)

    def collect_candidates(
        self,
        project_id: str,
        include_documents: bool = True,
        include_artifacts: bool = True,
    ) -> list[RetrievalCandidate]:
        candidates: list[RetrievalCandidate] = []
        if include_documents:
            rows = (
                self.session.query(DocumentChunk, DocumentSection, DocumentVersion, Document)
                .join(DocumentSection, DocumentChunk.section_id == DocumentSection.id)
                .join(DocumentVersion, DocumentChunk.document_version_id == DocumentVersion.id)
                .join(Document, DocumentVersion.document_id == Document.id)
                .filter(Document.project_id == project_id)
                .all()
            )
            for chunk, section, _version, document in rows:
                candidates.append(
                    RetrievalCandidate(
                        source_type="document_chunk",
                        source_id=chunk.id,
                        project_id=document.project_id,
                        title=document.title,
                        text=chunk.text,
                        heading_path_text=section.heading_path_text,
                        heading_path_ltree=section.heading_path_ltree,
                    )
                )
        if include_artifacts:
            for artifact in self.session.query(Artifact).filter(Artifact.project_id == project_id).all():
                candidates.append(
                    RetrievalCandidate(
                        source_type="artifact",
                        source_id=artifact.id,
                        project_id=artifact.project_id,
                        title=artifact.title,
                        text=artifact.index_projection.get("text") or artifact.rendered_markdown,
                    )
                )
        return candidates
