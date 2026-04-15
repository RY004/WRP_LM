"""Normalized artifact validation helpers."""

from typing import Any

from pydantic import ValidationError

from saturn.artifacts.normalized.schema import NormalizedArtifact


def validate_normalized_artifact(value: dict[str, Any]) -> dict[str, Any]:
    try:
        normalized = NormalizedArtifact.model_validate(value)
    except ValidationError as exc:
        raise ValueError(f"Invalid normalized artifact: {exc}") from exc

    for index, block in enumerate(normalized.blocks):
        if block.type in {"heading", "paragraph", "code"} and not block.text:
            raise ValueError(f"Block {index} requires text")
        if block.type == "heading" and block.level is None:
            raise ValueError(f"Heading block {index} requires level")
        if block.type == "list" and not block.items:
            raise ValueError(f"List block {index} requires items")

    return normalized.model_dump(mode="json")
