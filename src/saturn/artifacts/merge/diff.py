"""Artifact diff primitives."""

from typing import Any


def diff_normalized(left: dict[str, Any], right: dict[str, Any]) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    for key in ("title", "metadata"):
        if left.get(key) != right.get(key):
            changes.append({"path": f"/{key}", "left": left.get(key), "right": right.get(key)})

    left_blocks = left.get("blocks", [])
    right_blocks = right.get("blocks", [])
    max_len = max(len(left_blocks), len(right_blocks))
    for index in range(max_len):
        path = f"/blocks/{index}"
        if index >= len(left_blocks):
            changes.append({"path": path, "left": None, "right": right_blocks[index]})
        elif index >= len(right_blocks):
            changes.append({"path": path, "left": left_blocks[index], "right": None})
        elif left_blocks[index] != right_blocks[index]:
            changes.append({"path": path, "left": left_blocks[index], "right": right_blocks[index]})
    return changes
