"""Document parser registry."""

from saturn.documents.parsing.adapters.base import ParserAdapter
from saturn.documents.parsing.adapters.docling import DoclingParser
from saturn.documents.parsing.adapters.json_native import NativeJsonParser
from saturn.documents.parsing.adapters.markitdown_fallback import MarkItDownFallbackParser
from saturn.documents.parsing.adapters.tree_sitter import TreeSitterParser


class ParserRegistry:
    def __init__(self, parsers: list[ParserAdapter] | None = None) -> None:
        self.parsers = parsers or [
            NativeJsonParser(),
            DoclingParser(),
            TreeSitterParser(),
            MarkItDownFallbackParser(),
        ]

    def parser_for(self, filename: str, media_type: str) -> ParserAdapter:
        for parser in self.parsers:
            if parser.supports(filename, media_type):
                return parser
        return MarkItDownFallbackParser()


def default_parser_registry() -> ParserRegistry:
    return ParserRegistry()
