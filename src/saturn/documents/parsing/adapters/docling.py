"""Docling parser adapter with degraded PDF/DOCX behavior."""

from saturn.documents.parsing.adapters.base import ParseDiagnosticItem, ParseOutput, ParsedSection


class DoclingParser:
    name = "docling"

    def supports(self, filename: str, media_type: str) -> bool:
        lower = filename.lower()
        return lower.endswith((".pdf", ".docx")) or media_type in {
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }

    def parse(self, payload: bytes, filename: str, media_type: str) -> ParseOutput:
        text = payload.decode("utf-8", errors="ignore").strip()
        diagnostics = [
            ParseDiagnosticItem(
                severity="warning",
                code="docling_unavailable",
                message="Docling runtime is not installed; persisted degraded parse output for follow-up.",
            )
        ]
        body = text if text else f"Binary source registered for {filename}; full extraction is deferred."
        section = ParsedSection(
            title=filename or "Document",
            body=body,
            level=1,
            metadata={"degraded": True, "media_type": media_type},
        )
        return ParseOutput(
            parser_name=self.name,
            status="partial",
            normalized_tree={
                "type": "document",
                "source": filename,
                "degraded": True,
                "sections": [{"title": section.title, "body": section.body, "level": 1}],
            },
            rendered_markdown=f"# {section.title}\n\n{section.body}\n",
            sections=[section],
            diagnostics=diagnostics,
        )
