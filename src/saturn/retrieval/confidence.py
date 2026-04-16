"""Confidence band derivation."""


def confidence_band(score: float, degraded: bool = False) -> str:
    if degraded:
        if score >= 0.75:
            return "medium"
        return "low"
    if score >= 0.75:
        return "high"
    if score >= 0.35:
        return "medium"
    return "low"
