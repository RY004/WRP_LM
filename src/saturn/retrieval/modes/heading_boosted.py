"""Heading-boosted retrieval mode."""

from saturn.retrieval.repository import RetrievalCandidate


def heading_boost(query: str, candidate: RetrievalCandidate) -> float:
    heading = (candidate.heading_path_text or candidate.title).lower()
    terms = [term for term in query.lower().split() if term]
    if not terms:
        return 0.0
    matches = sum(1 for term in terms if term in heading)
    return min(0.2, matches * 0.08)
