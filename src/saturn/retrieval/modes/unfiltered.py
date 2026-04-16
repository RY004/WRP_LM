"""Unfiltered retrieval mode."""

from saturn.retrieval.repository import RetrievalCandidate


def apply_unfiltered(candidates: list[RetrievalCandidate]) -> list[RetrievalCandidate]:
    return candidates
