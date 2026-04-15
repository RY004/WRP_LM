from saturn.artifacts.merge.three_way import three_way_merge
from saturn.artifacts.rendering.markdown import markdown_to_normalized, render_markdown


def test_markdown_round_trip_projection() -> None:
    normalized = markdown_to_normalized("# Brief\n\n## Goal\n\nShip it.\n\n- One\n- Two\n")

    assert normalized["title"] == "Brief"
    assert normalized["blocks"][0]["type"] == "heading"
    assert "- One" in render_markdown(normalized)


def test_three_way_merge_append_only_sections() -> None:
    base = {"schema_version": "saturn.normalized.v1", "title": "Plan", "blocks": []}
    left = {
        **base,
        "blocks": [{"type": "paragraph", "text": "Left note"}],
    }
    right = {
        **base,
        "blocks": [{"type": "paragraph", "text": "Right note"}],
    }

    result = three_way_merge(base, left, right)

    assert result["summary"]["clean"] is True
    assert len(result["merged"]["blocks"]) == 2


def test_three_way_merge_scalar_conflict_uses_right_and_reports() -> None:
    base = {"schema_version": "saturn.normalized.v1", "title": "Plan", "blocks": []}
    left = {**base, "title": "Left"}
    right = {**base, "title": "Right"}

    result = three_way_merge(base, left, right)

    assert result["merged"]["title"] == "Right"
    assert result["summary"]["conflict_count"] == 1
