"""Markdown projection and ingestion for normalized artifacts."""

from typing import Any

from saturn.artifacts.normalized.validate import validate_normalized_artifact


def render_markdown(normalized: dict[str, Any]) -> str:
    document = validate_normalized_artifact(normalized)
    lines: list[str] = [f"# {document['title']}", ""]
    for block in document["blocks"]:
        block_type = block["type"]
        if block_type == "heading":
            level = max(1, min(6, int(block.get("level") or 2)))
            lines.extend([f"{'#' * level} {block['text']}", ""])
        elif block_type == "paragraph":
            lines.extend([block["text"], ""])
        elif block_type == "list":
            lines.extend([f"- {item}" for item in block["items"]])
            lines.append("")
        elif block_type == "code":
            language = block.get("language") or ""
            lines.extend([f"```{language}", block["text"], "```", ""])
    return "\n".join(lines).strip() + "\n"


def markdown_to_normalized(markdown: str, title: str | None = None) -> dict[str, Any]:
    lines = markdown.splitlines()
    blocks: list[dict[str, Any]] = []
    paragraph: list[str] = []
    list_items: list[str] = []
    code_lines: list[str] | None = None
    code_language: str | None = None
    inferred_title = title

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            blocks.append({"type": "paragraph", "text": " ".join(paragraph)})
            paragraph = []

    def flush_list() -> None:
        nonlocal list_items
        if list_items:
            blocks.append({"type": "list", "items": list_items})
            list_items = []

    for raw_line in lines:
        line = raw_line.rstrip()
        if code_lines is not None:
            if line.startswith("```"):
                blocks.append(
                    {"type": "code", "text": "\n".join(code_lines), "language": code_language}
                )
                code_lines = None
                code_language = None
            else:
                code_lines.append(line)
            continue
        if line.startswith("```"):
            flush_paragraph()
            flush_list()
            code_lines = []
            code_language = line[3:].strip() or None
            continue
        if not line.strip():
            flush_paragraph()
            flush_list()
            continue
        if line.startswith("#"):
            marker, _, text = line.partition(" ")
            if marker and set(marker) == {"#"} and text:
                flush_paragraph()
                flush_list()
                level = min(6, len(marker))
                if level == 1 and inferred_title is None:
                    inferred_title = text.strip()
                    continue
                blocks.append({"type": "heading", "level": level, "text": text.strip()})
                continue
        if line.startswith("- "):
            flush_paragraph()
            list_items.append(line[2:].strip())
            continue
        flush_list()
        paragraph.append(line.strip())

    if code_lines is not None:
        blocks.append({"type": "code", "text": "\n".join(code_lines), "language": code_language})
    flush_paragraph()
    flush_list()
    return validate_normalized_artifact(
        {"schema_version": "saturn.normalized.v1", "title": inferred_title or "Untitled", "blocks": blocks}
    )
