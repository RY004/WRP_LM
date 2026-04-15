"""Comment workflow service."""

from sqlalchemy.orm import Session

from saturn.access.context import AuthContext
from saturn.access.policies import Permission, require_authenticated
from saturn.access.service import AccessService
from saturn.artifacts.repository import ArtifactRepository
from saturn.collaboration.db_models import ArtifactComment, StageComment
from saturn.collaboration.repository import CollaborationRepository
from saturn.shared.time import utc_now


class CommentsService:
    def __init__(self, session: Session) -> None:
        self.repository = CollaborationRepository(session)
        self.artifacts = ArtifactRepository(session)
        self.access = AccessService(session)

    def create_artifact_comment(
        self, context: AuthContext, artifact_id: str, body: str, version_id: str | None = None
    ) -> ArtifactComment:
        user_id = require_authenticated(context)
        artifact = self.artifacts.get(artifact_id)
        if artifact is None:
            raise LookupError("Artifact not found")
        self.access.require_project_permission(context, artifact.project_id, Permission.PROJECT_READ)
        return self.repository.add_artifact_comment(
            ArtifactComment(
                artifact_id=artifact_id,
                version_id=version_id,
                body=body,
                created_by_user_id=user_id,
                updated_by_user_id=user_id,
            )
        )

    def list_artifact_comments(self, context: AuthContext, artifact_id: str) -> list[ArtifactComment]:
        artifact = self.artifacts.get(artifact_id)
        if artifact is None:
            raise LookupError("Artifact not found")
        self.access.require_project_permission(context, artifact.project_id, Permission.PROJECT_READ)
        return self.repository.list_artifact_comments(artifact_id)

    def update_artifact_comment(
        self, context: AuthContext, comment_id: str, body: str
    ) -> ArtifactComment:
        user_id = require_authenticated(context)
        comment = self.repository.get_artifact_comment(comment_id)
        if comment is None or comment.status != "active":
            raise LookupError("Artifact comment not found")
        if comment.created_by_user_id != user_id:
            raise PermissionError("Only the comment author can edit this comment")
        comment.body = body
        comment.updated_by_user_id = user_id
        return comment

    def delete_artifact_comment(self, context: AuthContext, comment_id: str) -> None:
        user_id = require_authenticated(context)
        comment = self.repository.get_artifact_comment(comment_id)
        if comment is None or comment.status != "active":
            raise LookupError("Artifact comment not found")
        if comment.created_by_user_id != user_id:
            raise PermissionError("Only the comment author can delete this comment")
        comment.status = "deleted"
        comment.deleted_at = utc_now()

    def create_stage_comment(
        self, context: AuthContext, project_id: str, stage: str, body: str
    ) -> StageComment:
        user_id = require_authenticated(context)
        self.access.require_project_permission(context, project_id, Permission.PROJECT_READ)
        return self.repository.add_stage_comment(
            StageComment(
                project_id=project_id,
                stage=stage,
                body=body,
                created_by_user_id=user_id,
                updated_by_user_id=user_id,
            )
        )

    def list_stage_comments(
        self, context: AuthContext, project_id: str, stage: str
    ) -> list[StageComment]:
        self.access.require_project_permission(context, project_id, Permission.PROJECT_READ)
        return self.repository.list_stage_comments(project_id, stage)

    def update_stage_comment(self, context: AuthContext, comment_id: str, body: str) -> StageComment:
        user_id = require_authenticated(context)
        comment = self.repository.get_stage_comment(comment_id)
        if comment is None or comment.status != "active":
            raise LookupError("Stage comment not found")
        if comment.created_by_user_id != user_id:
            raise PermissionError("Only the comment author can edit this comment")
        comment.body = body
        comment.updated_by_user_id = user_id
        return comment

    def delete_stage_comment(self, context: AuthContext, comment_id: str) -> None:
        user_id = require_authenticated(context)
        comment = self.repository.get_stage_comment(comment_id)
        if comment is None or comment.status != "active":
            raise LookupError("Stage comment not found")
        if comment.created_by_user_id != user_id:
            raise PermissionError("Only the comment author can delete this comment")
        comment.status = "deleted"
        comment.deleted_at = utc_now()
