"""In-process MCP tool surface for Saturn agents."""

from typing import Any

from sqlalchemy.orm import Session

from saturn.mcp.auth import context_from_token
from saturn.mcp.toolsets.pipeline import pipeline_tools
from saturn.mcp.toolsets.rag import rag_tools
from saturn.mcp.toolsets.wiki import wiki_tools
from saturn.plugins.gateway import PluginGateway


class SaturnMCPServer:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.gateway = PluginGateway(session)
        self.tools = {
            tool.name: tool
            for tool in [
                *pipeline_tools(),
                *rag_tools(),
                *wiki_tools(),
            ]
        }

    def list_tools(self, session_token: str) -> list[dict[str, Any]]:
        context_from_token(self.session, session_token)
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
                "capability": tool.capability,
            }
            for tool in self.tools.values()
        ]

    def call_tool(
        self, session_token: str, plugin_key: str, tool_name: str, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        context = context_from_token(self.session, session_token)
        tool = self.tools.get(tool_name)
        if tool is None:
            raise LookupError("MCP tool not found")
        project_id = arguments["project_id"]
        execution, result = self.gateway.execute(
            context,
            plugin_key=plugin_key,
            project_id=project_id,
            capability=tool.capability,
            payload=tool.handler(arguments),
        )
        return {"execution_id": execution.id, "result": result}
