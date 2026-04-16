"""Service layer for retrieval."""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from saturn.access.context import AuthContext
from saturn.access.policies import Permission
from saturn.access.service import AccessService
from saturn.embeddings.service import EmbeddingService
from saturn.retrieval.api_models import RetrievalResponse, RetrievalResult
from saturn.retrieval.citations import citation_for
from saturn.retrieval.confidence import confidence_band
from saturn.retrieval.fusion import hybrid_score
from saturn.retrieval.lexical import lexical_score
from saturn.retrieval.modes.heading_boosted import heading_boost
from saturn.retrieval.modes.strict_section import apply_strict_section
from saturn.retrieval.repository import RetrievalCandidate, RetrievalRepository
from saturn.retrieval.vector import cosine_similarity


@dataclass(frozen=True, slots=True)
class ScoredCandidate:
    candidate: RetrievalCandidate
    lexical: float
    vector: float | None
    score: float


class RetrievalService:
    def __init__(self, session: Session, embedding_service: EmbeddingService | None = None) -> None:
        self.session = session
        self.repository = RetrievalRepository(session)
        self.embeddings = embedding_service or EmbeddingService(session)
        self.access = AccessService(session)

    def query(
        self,
        context: AuthContext,
        project_id: str,
        query: str,
        mode: str = "unfiltered",
        section_path_prefix: str | None = None,
        include_documents: bool = True,
        include_artifacts: bool = True,
        limit: int = 10,
    ) -> RetrievalResponse:
        self.access.require_project_permission(context, project_id, Permission.PROJECT_READ)
        candidates = self.repository.collect_candidates(
            project_id,
            include_documents=include_documents,
            include_artifacts=include_artifacts,
        )
        if mode == "strict_section":
            candidates = apply_strict_section(candidates, section_path_prefix)
        embedding_records = self.embeddings.repository.records_by_source(
            project_id,
            model_name=self.embeddings.backend.model_name,
        )
        degraded = len(embedding_records) == 0 and len(candidates) > 0
        diagnostics = ["vector_index_unavailable; lexical-only fallback used"] if degraded else []
        query_vector = None if degraded else self.embeddings.embed_query(query).values
        scored: list[ScoredCandidate] = []
        for candidate in candidates:
            lexical = lexical_score(query, candidate)
            record = embedding_records.get((candidate.source_type, candidate.source_id))
            vector = (
                cosine_similarity(query_vector, record.vector)
                if query_vector is not None and record is not None
                else None
            )
            boost = heading_boost(query, candidate) if mode == "heading_boosted" else 0.0
            score = hybrid_score(lexical, vector, heading_boost=boost)
            if score > 0:
                scored.append(ScoredCandidate(candidate, lexical, vector, score))
        scored.sort(key=lambda item: item.score, reverse=True)
        results = [
            RetrievalResult(
                source_type=item.candidate.source_type,
                source_id=item.candidate.source_id,
                title=item.candidate.title,
                text=item.candidate.text,
                score=round(item.score, 6),
                lexical_score=round(item.lexical, 6),
                vector_score=round(item.vector, 6) if item.vector is not None else None,
                confidence=confidence_band(item.score, degraded=degraded),
                citation=citation_for(item.candidate),
            )
            for item in scored[:limit]
        ]
        return RetrievalResponse(
            query=query,
            mode=mode,
            degraded=degraded,
            diagnostics=diagnostics,
            results=results,
        )
