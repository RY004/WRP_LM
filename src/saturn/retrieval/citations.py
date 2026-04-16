"""Citation assembly."""

from saturn.retrieval.api_models import RetrievalCitation
from saturn.retrieval.repository import RetrievalCandidate


def citation_for(candidate: RetrievalCandidate) -> RetrievalCitation:
    return RetrievalCitation(
        source_type=candidate.source_type,
        source_id=candidate.source_id,
        title=candidate.title,
        heading_path_text=candidate.heading_path_text,
        section_path=candidate.heading_path_ltree,
    )
