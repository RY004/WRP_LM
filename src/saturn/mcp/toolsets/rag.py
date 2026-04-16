"""Retrieval MCP tool definitions."""

from saturn.mcp.types import MCPTool


def rag_tools() -> list[MCPTool]:
    return [
        MCPTool(
            name="saturn_rag_query",
            description="Query project retrieval sources.",
            capability="rag.query",
            input_schema={
                "type": "object",
                "required": ["project_id", "query"],
                "properties": {
                    "project_id": {"type": "string"},
                    "query": {"type": "string"},
                    "mode": {"type": "string"},
                    "limit": {"type": "integer"},
                },
            },
            handler=lambda args: {
                "query": args["query"],
                "mode": args.get("mode", "unfiltered"),
                "limit": args.get("limit", 10),
                "include_documents": args.get("include_documents", True),
                "include_artifacts": args.get("include_artifacts", True),
                "section_path_prefix": args.get("section_path_prefix"),
            },
        )
    ]
