"""Wiki/artifact MCP tool definitions."""

from saturn.mcp.types import MCPTool


def wiki_tools() -> list[MCPTool]:
    return [
        MCPTool(
            name="saturn_wiki_list",
            description="List project artifacts.",
            capability="wiki.list",
            input_schema={"type": "object", "required": ["project_id"], "properties": {"project_id": {"type": "string"}}},
            handler=lambda args: {},
        ),
        MCPTool(
            name="saturn_wiki_get",
            description="Read one project artifact.",
            capability="wiki.get",
            input_schema={
                "type": "object",
                "required": ["project_id", "artifact_id"],
                "properties": {
                    "project_id": {"type": "string"},
                    "artifact_id": {"type": "string"},
                },
            },
            handler=lambda args: {"artifact_id": args["artifact_id"]},
        ),
    ]
