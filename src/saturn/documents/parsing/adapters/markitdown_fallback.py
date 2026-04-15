"""Markdown/plain-text parser used as a MarkItDown-compatible fallback."""

from saturn.documents.parsing.adapters.base import (
    ParseDiagnosticItem,
    ParseOutput,
    ParsedSection,
)


class MarkItDownFallbackParser:
    name = "markitdown_fallback"

    def supports(self, filename: str, media_type: str) -> bool:
        return True

    def parse(self, payload: bytes, filename: str, media_type: str) -> ParseOutput:
        text = payload.decode("utf-8", errors="replace")
        diagnostics: list[ParseDiagnosticItem] = []
        if "\ufffd" in text:
            diagnostics.append(
                ParseDiagnosticItem(
                    severity="warning",
                    code="decode_replacement",
                    message="Source contained bytes that were replaced during UTF-8 decoding.",
                )
            )
        sections = parse_markdown_sections(text, default_title=filename)
        return ParseOutput(
            parser_name=self.name,
            status="parsed" if not diagnostics else "partial",
            normalized_tree={"type": "document", "source": filename, "sections": _sections_to_dict(sections)},
            rendered_markdown=text,
            sections=sections,
            diagnostics=diagnostics,
        )


def parse_markdown_sections(markdown: str, default_title: str) -> list[ParsedSection]:
    roots: list[ParsedSection] = []
    stack: list[ParsedSection] = []
    current: ParsedSection | None = None
    body_lines: list[str] = []

    def flush_body() -> None:
        nonlocal body_lines
        if current is not None:
            current.body = "\n".join(body_lines).strip()
        body_lines = []

    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            marker = stripped.split(" ", 1)[0]
            if set(marker) == {"#"} and 1 <= len(marker) <= 6 and len(stripped) > len(marker):
                flush_body()
                level = len(marker)
                section = ParsedSection(title=stripped[len(marker) :].strip(), level=level)
                while stack and stack[-1].level >= level:
                    stack.pop()
                if stack:
                    stack[-1].children.append(section)
                else:
                    roots.append(section)
                stack.append(section)
                current = section
                continue
        body_lines.append(line)

    flush_body()
    if roots:
        return roots
    body = markdown.strip()
    return [ParsedSection(title=default_title or "Document", body=body, level=1)]


def _sections_to_dict(sections: list[ParsedSection]) -> list[dict]:
    return [
        {
            "title": section.title,
            "body": section.body,
            "level": section.level,
            "children": _sections_to_dict(section.children),
            "metadata": section.metadata,
        }
        for section in sections
    ]
