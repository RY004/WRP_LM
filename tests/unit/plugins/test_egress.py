import pytest

from saturn.access.context import AuthContext
from saturn.plugins.egress.allowlist import EgressDeniedError, PluginEgressAllowlist
from saturn.plugins.egress.policies import PluginEgressPolicyService
from saturn.plugins.registry import PluginRegistryService
from tests.api.test_phase7_plugins import _login
from fastapi.testclient import TestClient


def test_egress_defaults_deny_and_allowlist_records_decisions(phase2_app) -> None:
    client = TestClient(phase2_app)
    token, project_id = _login(client, email="phase7-egress@example.com")
    with phase2_app.state.container.session_factory() as session:
        context = _context_for_token(session, token)
        PluginRegistryService(session).register(
            context,
            key="egress-plugin",
            name="Egress Plugin",
            description=None,
            version="1.0.0",
            entrypoint="internal",
            manifest={},
            capabilities=[],
        )
        session.commit()

        allowlist = PluginEgressAllowlist(session)
        with pytest.raises(EgressDeniedError):
            allowlist.require_allowed(
                context,
                plugin_key="egress-plugin",
                project_id=project_id,
                url="https://example.com/data",
                method="GET",
            )

        PluginEgressPolicyService(session).create_policy(
            context,
            plugin_key="egress-plugin",
            project_id=project_id,
            scheme="https",
            host="example.com",
            methods=["GET"],
        )
        allowlist.require_allowed(
            context,
            plugin_key="egress-plugin",
            project_id=project_id,
            url="https://example.com/data",
            method="GET",
        )


def _context_for_token(session, token: str) -> AuthContext:
    from saturn.identity.service import IdentityService

    user_session = IdentityService(session).get_session(token)
    return AuthContext(
        user_id=user_session.user_id,
        org_id=user_session.org_id,
        session_id=token,
    )
