"""Three-way merge primitives for normalized artifacts."""

from copy import deepcopy
from typing import Any

from saturn.artifacts.merge.conflicts import MergeConflict
from saturn.artifacts.merge.summary import summarize_merge
from saturn.artifacts.normalized.validate import validate_normalized_artifact


def three_way_merge(
    base: dict[str, Any], left: dict[str, Any], right: dict[str, Any]
) -> dict[str, Any]:
    base_doc = validate_normalized_artifact(base)
    left_doc = validate_normalized_artifact(left)
    right_doc = validate_normalized_artifact(right)
    merged = deepcopy(base_doc)
    conflicts: list[MergeConflict] = []

    for key in ("title", "metadata"):
        base_value = base_doc.get(key)
        left_value = left_doc.get(key)
        right_value = right_doc.get(key)
        if left_value == right_value:
            merged[key] = deepcopy(left_value)
        elif left_value == base_value:
            merged[key] = deepcopy(right_value)
        elif right_value == base_value:
            merged[key] = deepcopy(left_value)
        else:
            merged[key] = deepcopy(right_value)
            conflicts.append(MergeConflict(f"/{key}", base_value, left_value, right_value, "scalar_conflict_last_write_wins"))

    base_blocks = base_doc.get("blocks", [])
    left_blocks = left_doc.get("blocks", [])
    right_blocks = right_doc.get("blocks", [])
    if left_blocks == right_blocks:
        merged["blocks"] = deepcopy(left_blocks)
    elif left_blocks == base_blocks:
        merged["blocks"] = deepcopy(right_blocks)
    elif right_blocks == base_blocks:
        merged["blocks"] = deepcopy(left_blocks)
    elif _is_append_only(base_blocks, left_blocks) and _is_append_only(base_blocks, right_blocks):
        appended = deepcopy(left_blocks)
        for block in right_blocks[len(base_blocks) :]:
            if block not in appended:
                appended.append(deepcopy(block))
        merged["blocks"] = appended
    else:
        merged["blocks"] = deepcopy(right_blocks)
        conflicts.append(
            MergeConflict("/blocks", base_blocks, left_blocks, right_blocks, "manual_block_conflict")
        )

    normalized = validate_normalized_artifact(merged)
    return {
        "merged": normalized,
        "conflicts": [
            {
                "path": conflict.path,
                "reason": conflict.reason,
                "base": conflict.base,
                "left": conflict.left,
                "right": conflict.right,
            }
            for conflict in conflicts
        ],
        "summary": summarize_merge(normalized, conflicts),
    }


def _is_append_only(base_blocks: list[dict[str, Any]], candidate: list[dict[str, Any]]) -> bool:
    return len(candidate) >= len(base_blocks) and candidate[: len(base_blocks)] == base_blocks
