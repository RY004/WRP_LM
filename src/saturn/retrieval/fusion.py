"""Hybrid retrieval score fusion."""


def hybrid_score(lexical: float, vector: float | None, heading_boost: float = 0.0) -> float:
    if vector is None:
        return min(1.0, lexical + heading_boost)
    return min(1.0, lexical * 0.45 + max(vector, 0.0) * 0.55 + heading_boost)
