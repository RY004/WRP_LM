"""Shared MCP surface types."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class MCPTool:
    name: str
    description: str
    input_schema: dict[str, Any]
    capability: str
    handler: Callable[[dict[str, Any]], dict[str, Any]]
