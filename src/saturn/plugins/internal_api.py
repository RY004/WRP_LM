"""Internal API dispatcher for plugin tools.

The dispatcher is intentionally thin: plugins can only reach domain services by
declaring a capability that maps to one of these methods.
"""

from sqlalchemy.orm import Session

from saturn.access.context import AuthContext
from saturn.plugins.domains.pipeline import PipelinePluginDomain
from saturn.plugins.domains.rag import RagPluginDomain
from saturn.plugins.domains.wiki import WikiPluginDomain


class InternalPluginAPI:
    def __init__(self, session: Session) -> None:
        self.domains = {
            "pipeline": PipelinePluginDomain(session),
            "rag": RagPluginDomain(session),
            "wiki": WikiPluginDomain(session),
        }

    def dispatch(
        self,
        context: AuthContext,
        project_id: str,
        domain: str,
        action: str,
        payload: dict,
    ) -> dict:
        if domain not in self.domains:
            raise ValueError(f"Unsupported plugin domain: {domain}")
        return self.domains[domain].dispatch(context, project_id, action, payload)
