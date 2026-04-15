"""Tree-sitter-style parser adapter for source code snapshots."""

from saturn.documents.parsing.adapters.base import ParseDiagnosticItem, ParseOutput, ParsedSection


CODE_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".go",
    ".rs",
    ".java",
    ".c",
    ".h",
    ".cpp",
    ".hpp",
    ".sql",
}


class TreeSitterParser:
    name = "tree_sitter"

    def supports(self, filename: str, media_type: str) -> bool:
        lower = filename.lower()
        return media_type.startswith("text/x-") or any(lower.endswith(ext) for ext in CODE_EXTENSIONS)

    def parse(self, payload: bytes, filename: str, media_type: str) -> ParseOutput:
        text = payload.decode("utf-8", errors="replace")
        diagnostics = [
            ParseDiagnosticItem(
                severity="info",
                code="tree_sitter_degraded",
                message="Source snapshot parsed with line-oriented fallback until grammar bundles are installed.",
            )
        ]
        section = ParsedSection(
            title=filename or "Code snapshot",
            body=text,
            level=1,
            metadata={"content_type": "code", "media_type": media_type},
        )
        rendered = f"# {section.title}\n\n```\n{text}\n```\n"
        return ParseOutput(
            parser_name=self.name,
            status="partial",
            normalized_tree={
                "type": "document",
                "source": filename,
                "language": _language_from_filename(filename),
                "sections": [{"title": section.title, "body": text, "level": 1}],
            },
            rendered_markdown=rendered,
            sections=[section],
            diagnostics=diagnostics,
        )


def _language_from_filename(filename: str) -> str | None:
    suffix = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".jsx": "javascript",
        ".go": "go",
        ".rs": "rust",
        ".java": "java",
        ".sql": "sql",
    }.get(suffix)
