"""Parser adapter contracts and normalized parse structures."""

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable


@dataclass(slots=True)
class ParseDiagnosticItem:
    severity: str
    code: str
    message: str
    details: dict = field(default_factory=dict)


@dataclass(slots=True)
class ParsedSection:
    title: str
    body: str = ""
    level: int = 1
    children: list["ParsedSection"] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


@dataclass(slots=True)
class ParseOutput:
    parser_name: str
    status: str
    normalized_tree: dict
    rendered_markdown: str
    sections: list[ParsedSection]
    diagnostics: list[ParseDiagnosticItem] = field(default_factory=list)


@runtime_checkable
class ParserAdapter(Protocol):
    name: str

    def supports(self, filename: str, media_type: str) -> bool: ...

    def parse(self, payload: bytes, filename: str, media_type: str) -> ParseOutput: ...
