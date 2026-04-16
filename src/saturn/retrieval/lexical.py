"""Lexical retrieval scoring."""

import re

from saturn.retrieval.repository import RetrievalCandidate


def lexical_score(query: str, candidate: RetrievalCandidate) -> float:
    query_terms = _terms(query)
    if not query_terms:
        return 0.0
    text_terms = _terms(" ".join([candidate.title, candidate.heading_path_text or "", candidate.text]))
    if not text_terms:
        return 0.0
    matches = sum(1 for term in query_terms if term in text_terms)
    coverage = matches / len(query_terms)
    density = matches / max(len(text_terms), 1)
    return min(1.0, coverage * 0.85 + density * 3.0)


def _terms(value: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9_]+", value.lower())
