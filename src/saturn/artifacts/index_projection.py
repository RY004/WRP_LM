"""Artifact projection helpers for retrieval and export."""

from typing import Any

from saturn.artifacts.rendering.markdown import render_markdown


def build_index_projection(artifact_id: str, normalized: dict[str, Any]) -> dict[str, Any]:
    markdown = render_markdown(normalized)
    headings = [
        {"level": block.get("level"), "text": block.get("text")}
        for block in normalized.get("blocks", [])
        if block.get("type") == "heading"
    ]
    return {
        "artifact_id": artifact_id,
        "title": normalized["title"],
        "headings": headings,
        "text": markdown,
        "schema_version": normalized["schema_version"],
    }
