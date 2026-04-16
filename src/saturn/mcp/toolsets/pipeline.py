"""Pipeline MCP tool definitions."""

from saturn.mcp.types import MCPTool


def pipeline_tools() -> list[MCPTool]:
    return [
        MCPTool(
            name="saturn_pipeline_get",
            description="Read project pipeline state.",
            capability="pipeline.get",
            input_schema={"type": "object", "required": ["project_id"], "properties": {"project_id": {"type": "string"}}},
            handler=lambda args: {},
        ),
        MCPTool(
            name="saturn_pipeline_handoff",
            description="Read the project handoff packet.",
            capability="pipeline.handoff",
            input_schema={"type": "object", "required": ["project_id"], "properties": {"project_id": {"type": "string"}}},
            handler=lambda args: {},
        ),
    ]
