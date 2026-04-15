"""Pipeline rule evaluation."""

STAGE_ORDER = (
    "question",
    "research",
    "structure",
    "plan",
    "implement",
    "validate",
    "release",
)


def next_stage(current_stage: str) -> str | None:
    try:
        index = STAGE_ORDER.index(current_stage)
    except ValueError as exc:
        raise ValueError(f"Unknown pipeline stage: {current_stage}") from exc
    if index + 1 >= len(STAGE_ORDER):
        return None
    return STAGE_ORDER[index + 1]


def can_advance(status: str, override: bool = False) -> bool:
    return override or status in {"active", "approved", "rejected"}
