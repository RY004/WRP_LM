"""Strict-section retrieval mode."""

from saturn.retrieval.repository import RetrievalCandidate


def apply_strict_section(
    candidates: list[RetrievalCandidate], section_path_prefix: str | None
) -> list[RetrievalCandidate]:
    if not section_path_prefix:
        return candidates
    normalized = section_path_prefix.lower()
    return [
        candidate
        for candidate in candidates
        if (candidate.heading_path_text or "").lower().startswith(normalized)
        or (candidate.heading_path_ltree or "").lower().startswith(normalized)
    ]
