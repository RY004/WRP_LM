"""API-mediated wiki/artifact plugin domain."""

from sqlalchemy.orm import Session

from saturn.access.context import AuthContext
from saturn.artifacts.service import ArtifactService


class WikiPluginDomain:
    def __init__(self, session: Session) -> None:
        self.service = ArtifactService(session)

    def dispatch(self, context: AuthContext, project_id: str, action: str, payload: dict) -> dict:
        if action == "list":
            return {
                "artifacts": [
                    {
                        "id": artifact.id,
                        "slug": artifact.slug,
                        "title": artifact.title,
                        "artifact_type": artifact.artifact_type,
                        "status": artifact.status,
                    }
                    for artifact in self.service.list_artifacts(context, project_id)
                ]
            }
        if action == "get":
            artifact = self.service.get_artifact(context, payload["artifact_id"])
            if artifact.project_id != project_id:
                raise PermissionError("Artifact is outside project scope")
            return {
                "id": artifact.id,
                "slug": artifact.slug,
                "title": artifact.title,
                "artifact_type": artifact.artifact_type,
                "status": artifact.status,
                "normalized_content": artifact.normalized_content,
                "rendered_markdown": artifact.rendered_markdown,
            }
        if action == "create":
            artifact = self.service.create_artifact(
                context,
                project_id=project_id,
                title=payload["title"],
                artifact_type=payload.get("artifact_type", "document"),
                normalized_content=payload.get("normalized_content"),
                markdown=payload.get("markdown"),
                slug=payload.get("slug"),
                stage=payload.get("stage"),
                lock_token=payload.get("lock_token"),
            )
            return {"id": artifact.id, "slug": artifact.slug, "version": artifact.current_version_number}
        if action == "update":
            artifact = self.service.update_artifact(
                context,
                artifact_id=payload["artifact_id"],
                title=payload.get("title"),
                status=payload.get("status"),
                normalized_content=payload.get("normalized_content"),
                markdown=payload.get("markdown"),
                change_summary=payload.get("change_summary"),
                stage=payload.get("stage"),
                lock_token=payload.get("lock_token"),
            )
            if artifact.project_id != project_id:
                raise PermissionError("Artifact is outside project scope")
            return {"id": artifact.id, "version": artifact.current_version_number}
        raise ValueError(f"Unsupported wiki action: {action}")
