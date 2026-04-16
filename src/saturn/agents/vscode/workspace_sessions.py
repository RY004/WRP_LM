"""VS Code workspace session service."""

from sqlalchemy.orm import Session

from saturn.access.context import AuthContext
from saturn.access.policies import Permission
from saturn.access.service import AccessService
from saturn.agents.vscode.capabilities import advertised_capabilities
from saturn.agents.vscode.token_exchange import VSCodeTokenExchangeService
from saturn.plugins.db_models import VSCodeWorkspaceSession
from saturn.plugins.repository import PluginRepository


class VSCodeWorkspaceSessionService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = PluginRepository(session)
        self.access = AccessService(session)
        self.exchanges = VSCodeTokenExchangeService(session)

    def create_or_get(
        self,
        exchange_token: str,
        project_id: str,
        workspace_uri: str,
        agent_id: str | None,
    ) -> VSCodeWorkspaceSession:
        exchange = self.exchanges.consume_exchange(exchange_token)
        context = AuthContext(
            user_id=exchange.user_id,
            org_id=exchange.org_id,
            session_id=exchange.session_token,
        )
        self.access.require_project_permission(context, project_id, Permission.PROJECT_READ)
        existing = self.repository.get_workspace_session(project_id, workspace_uri, exchange.user_id)
        if existing is not None:
            existing.agent_id = agent_id or existing.agent_id
            existing.status = "active"
            existing.capabilities = advertised_capabilities()
            self.session.flush()
            return existing
        row = self.repository.add(
            VSCodeWorkspaceSession(
                project_id=project_id,
                org_id=exchange.org_id,
                user_id=exchange.user_id,
                workspace_uri=workspace_uri,
                agent_id=agent_id,
                capabilities=advertised_capabilities(),
            )
        )
        self.session.flush()
        return row
