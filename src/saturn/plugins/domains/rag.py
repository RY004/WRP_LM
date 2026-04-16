"""API-mediated retrieval plugin domain."""

from sqlalchemy.orm import Session

from saturn.access.context import AuthContext
from saturn.retrieval.service import RetrievalService


class RagPluginDomain:
    def __init__(self, session: Session) -> None:
        self.service = RetrievalService(session)

    def dispatch(self, context: AuthContext, project_id: str, action: str, payload: dict) -> dict:
        if action != "query":
            raise ValueError(f"Unsupported rag action: {action}")
        response = self.service.query(
            context,
            project_id=project_id,
            query=payload.get("query", ""),
            mode=payload.get("mode", "unfiltered"),
            section_path_prefix=payload.get("section_path_prefix"),
            include_documents=payload.get("include_documents", True),
            include_artifacts=payload.get("include_artifacts", True),
            limit=payload.get("limit", 10),
        )
        return response.model_dump()
