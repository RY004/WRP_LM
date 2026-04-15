"""Artifact merge summary helpers."""

from typing import Any

from saturn.artifacts.merge.conflicts import MergeConflict


def summarize_merge(result: dict[str, Any], conflicts: list[MergeConflict]) -> dict[str, Any]:
    return {
        "clean": not conflicts,
        "conflict_count": len(conflicts),
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
        "block_count": len(result.get("blocks", [])),
    }
