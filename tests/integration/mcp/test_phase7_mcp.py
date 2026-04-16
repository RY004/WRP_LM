from fastapi.testclient import TestClient
import pytest

from saturn.mcp.server import SaturnMCPServer
from saturn.plugins.registry import PluginRegistryService
from tests.api.test_phase7_plugins import _login


def test_mcp_tool_shape_auth_and_gateway_call(phase2_app) -> None:
    client = TestClient(phase2_app)
    token, project_id = _login(client, email="phase7-mcp@example.com")

    with phase2_app.state.container.session_factory() as session:
        context = _context_for_token(session, token)
        PluginRegistryService(session).register(
            context,
            key="mcp-plugin",
            name="MCP Plugin",
            description=None,
            version="1.0.0",
            entrypoint="internal",
            manifest={},
            capabilities=[
                _capability("pipeline.get", "pipeline"),
                _capability("rag.query", "rag"),
                _capability("wiki.list", "wiki"),
            ],
        )
        PluginRegistryService(session).install(
            context, "mcp-plugin", "1.0.0", project_id=project_id, enabled=True
        )
        session.commit()

        server = SaturnMCPServer(session)
        with pytest.raises(PermissionError):
            server.list_tools("not-a-session")
        tools = server.list_tools(token)
        assert {tool["name"] for tool in tools} >= {"saturn_pipeline_get", "saturn_rag_query"}

        result = server.call_tool(
            token,
            plugin_key="mcp-plugin",
            tool_name="saturn_pipeline_get",
            arguments={"project_id": project_id},
        )
        assert result["result"]["project_id"] == project_id


def _context_for_token(session, token: str):
    from saturn.access.context import AuthContext
    from saturn.identity.service import IdentityService

    user_session = IdentityService(session).get_session(token)
    return AuthContext(user_id=user_session.user_id, org_id=user_session.org_id, session_id=token)


def _capability(capability: str, domain: str):
    from saturn.plugins.api_models import PluginCapabilityDecl

    return PluginCapabilityDecl(capability=capability, domain=domain)
