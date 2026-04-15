"""Native JSON document parser."""

import json

from saturn.documents.parsing.adapters.base import ParseDiagnosticItem, ParseOutput, ParsedSection


class NativeJsonParser:
    name = "native_json"

    def supports(self, filename: str, media_type: str) -> bool:
        return filename.lower().endswith(".json") or media_type in {
            "application/json",
            "application/x-json",
        }

    def parse(self, payload: bytes, filename: str, media_type: str) -> ParseOutput:
        try:
            data = json.loads(payload.decode("utf-8"))
        except Exception as exc:
            return ParseOutput(
                parser_name=self.name,
                status="failed",
                normalized_tree={"type": "document", "source": filename, "sections": []},
                rendered_markdown="",
                sections=[],
                diagnostics=[
                    ParseDiagnosticItem(
                        severity="error",
                        code="invalid_json",
                        message=f"JSON parse failed: {exc}",
                    )
                ],
            )
        section = ParsedSection(
            title=filename or "JSON document",
            body=json.dumps(data, indent=2, sort_keys=True),
            level=1,
            metadata={"content_type": "json"},
        )
        markdown = f"# {section.title}\n\n```json\n{section.body}\n```\n"
        return ParseOutput(
            parser_name=self.name,
            status="parsed",
            normalized_tree={"type": "document", "source": filename, "json": data},
            rendered_markdown=markdown,
            sections=[section],
        )
