"""VS Code capability negotiation."""

DEFAULT_VSCODE_CAPABILITIES = [
    "pipeline.get",
    "pipeline.handoff",
    "rag.query",
    "wiki.list",
    "wiki.get",
]


def advertised_capabilities(extra: list[str] | None = None) -> list[str]:
    capabilities = set(DEFAULT_VSCODE_CAPABILITIES)
    capabilities.update(extra or [])
    return sorted(capabilities)
