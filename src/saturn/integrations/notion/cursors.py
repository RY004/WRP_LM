"""Notion cursor helpers."""


def cursor_has_changed(previous: str | None, current: str) -> bool:
    return previous != current
