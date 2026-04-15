from saturn.documents.parsing.registry import ParserRegistry
from saturn.documents.parsing.section_paths import heading_path_ltree, heading_path_text


def test_markdown_parser_preserves_heading_hierarchy() -> None:
    parser = ParserRegistry().parser_for("notes.md", "text/markdown")

    output = parser.parse(b"# Alpha\n\nIntro\n\n## Beta\n\nDetails", "notes.md", "text/markdown")

    assert output.status == "parsed"
    assert output.sections[0].title == "Alpha"
    assert output.sections[0].children[0].title == "Beta"
    assert output.rendered_markdown.startswith("# Alpha")


def test_json_parser_keeps_native_json() -> None:
    parser = ParserRegistry().parser_for("data.json", "application/json")

    output = parser.parse(b'{"title": "Saturn", "items": [1]}', "data.json", "application/json")

    assert output.status == "parsed"
    assert output.parser_name == "native_json"
    assert output.normalized_tree["json"]["title"] == "Saturn"
    assert "```json" in output.rendered_markdown


def test_code_and_pdf_parsers_return_degraded_diagnostics() -> None:
    code = ParserRegistry().parser_for("app.py", "text/x-python")
    pdf = ParserRegistry().parser_for("brief.pdf", "application/pdf")

    code_output = code.parse(b"def main():\n    return 1", "app.py", "text/x-python")
    pdf_output = pdf.parse(b"%PDF placeholder", "brief.pdf", "application/pdf")

    assert code_output.status == "partial"
    assert code_output.diagnostics[0].code == "tree_sitter_degraded"
    assert pdf_output.status == "partial"
    assert pdf_output.diagnostics[0].code == "docling_unavailable"


def test_heading_paths_are_text_and_ltree_compatible() -> None:
    parts = ["1. Intro", "API & Workers"]

    assert heading_path_text(parts) == "1. Intro > API & Workers"
    assert heading_path_ltree(parts) == "s_1_intro.api_workers"
