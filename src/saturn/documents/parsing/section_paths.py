"""Helpers for stable section heading paths."""

import re


def heading_path_text(parts: list[str]) -> str:
    return " > ".join(part.strip() for part in parts if part.strip())


def heading_path_ltree(parts: list[str]) -> str:
    labels = [_ltree_label(part) for part in parts if part.strip()]
    return ".".join(label for label in labels if label) or "root"


def _ltree_label(value: str) -> str:
    label = re.sub(r"[^A-Za-z0-9_]+", "_", value.strip().lower()).strip("_")
    if not label:
        return "section"
    if label[0].isdigit():
        return f"s_{label}"
    return label[:200]
