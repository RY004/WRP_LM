"""Service layer for artifacts."""

import re
from typing import Any

from sqlalchemy.orm import Session

from saturn.access.context import AuthContext
from saturn.access.policies import Permission, require_authenticated
from saturn.access.service import AccessService
from saturn.artifacts.db_models import Artifact, ArtifactVersion
from saturn.artifacts.index_projection import build_index_projection
from saturn.artifacts.merge.three_way import three_way_merge
from saturn.artifacts.normalized.validate import validate_normalized_artifact
from saturn.artifacts.rendering.markdown import markdown_to_normalized, render_markdown
from saturn.artifacts.repository import ArtifactRepository
from saturn.collaboration.phase_lock_service import PhaseLockService


def artifact_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "artifact"


class ArtifactService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = ArtifactRepository(session)
        self.access = AccessService(session)
        self.phase_locks = PhaseLockService(session)

    def create_artifact(
        self,
        context: AuthContext,
        project_id: str,
        title: str,
        artifact_type: str,
        normalized_content: dict[str, Any] | None = None,
        markdown: str | None = None,
        slug: str | None = None,
        stage: str | None = None,
        lock_token: str | None = None,
    ) -> Artifact:
        user_id = require_authenticated(context)
        self.access.require_project_permission(context, project_id, Permission.PROJECT_WRITE)
        self.phase_locks.require_writable(context, project_id, stage, lock_token)
        content = self._normalize(title, normalized_content, markdown)
        artifact = Artifact(
            project_id=project_id,
            slug=slug or artifact_slug(title),
            title=content["title"],
            artifact_type=artifact_type,
            status="draft",
            normalized_content=content,
            rendered_markdown=render_markdown(content),
            index_projection={},
            created_by_user_id=user_id,
            updated_by_user_id=user_id,
        )
        self.repository.create(artifact)
        self.session.flush()
        artifact.index_projection = build_index_projection(artifact.id, content)
        version = self._create_version(artifact, content, user_id, "Initial version")
        artifact.current_version_id = version.id
        artifact.current_version_number = version.version_number
        return artifact

    def list_artifacts(self, context: AuthContext, project_id: str) -> list[Artifact]:
        self.access.require_project_permission(context, project_id, Permission.PROJECT_READ)
        return self.repository.list_for_project(project_id)

    def get_artifact(self, context: AuthContext, artifact_id: str) -> Artifact:
        artifact = self.repository.get(artifact_id)
        if artifact is None:
            raise LookupError("Artifact not found")
        self.access.require_project_permission(context, artifact.project_id, Permission.PROJECT_READ)
        return artifact

    def update_artifact(
        self,
        context: AuthContext,
        artifact_id: str,
        title: str | None = None,
        status: str | None = None,
        normalized_content: dict[str, Any] | None = None,
        markdown: str | None = None,
        change_summary: str | None = None,
        stage: str | None = None,
        lock_token: str | None = None,
    ) -> Artifact:
        user_id = require_authenticated(context)
        artifact = self.get_artifact(context, artifact_id)
        self.access.require_project_permission(context, artifact.project_id, Permission.PROJECT_WRITE)
        self.phase_locks.require_writable(context, artifact.project_id, stage, lock_token)
        if title is not None:
            artifact.title = title
        if status is not None:
            artifact.status = status
        if normalized_content is not None or markdown is not None:
            content = self._normalize(title or artifact.title, normalized_content, markdown)
            artifact.title = content["title"]
            artifact.normalized_content = content
            artifact.rendered_markdown = render_markdown(content)
            artifact.index_projection = build_index_projection(artifact.id, content)
            version = self._create_version(artifact, content, user_id, change_summary)
            artifact.current_version_id = version.id
            artifact.current_version_number = version.version_number
        artifact.updated_by_user_id = user_id
        return artifact

    def create_version(
        self,
        context: AuthContext,
        artifact_id: str,
        normalized_content: dict[str, Any] | None = None,
        markdown: str | None = None,
        change_summary: str | None = None,
        stage: str | None = None,
        lock_token: str | None = None,
    ) -> ArtifactVersion:
        artifact = self.update_artifact(
            context,
            artifact_id,
            normalized_content=normalized_content,
            markdown=markdown,
            change_summary=change_summary,
            stage=stage,
            lock_token=lock_token,
        )
        return self.repository.get_version(artifact.id, artifact.current_version_number)

    def get_version(self, context: AuthContext, artifact_id: str, version_number: int) -> ArtifactVersion:
        artifact = self.get_artifact(context, artifact_id)
        version = self.repository.get_version(artifact.id, version_number)
        if version is None:
            raise LookupError("Artifact version not found")
        return version

    def list_versions(self, context: AuthContext, artifact_id: str) -> list[ArtifactVersion]:
        artifact = self.get_artifact(context, artifact_id)
        return self.repository.list_versions(artifact.id)

    def merge(self, context: AuthContext, base: dict[str, Any], left: dict[str, Any], right: dict[str, Any]):
        require_authenticated(context)
        return three_way_merge(base, left, right)

    def _create_version(
        self, artifact: Artifact, content: dict[str, Any], user_id: str, change_summary: str | None
    ) -> ArtifactVersion:
        version_number = artifact.current_version_number + 1
        version = ArtifactVersion(
            artifact_id=artifact.id,
            version_number=version_number,
            normalized_content=content,
            rendered_markdown=render_markdown(content),
            index_projection=build_index_projection(artifact.id, content),
            change_summary=change_summary,
            created_by_user_id=user_id,
        )
        self.repository.create_version(version)
        self.session.flush()
        return version

    def _normalize(
        self, title: str, normalized_content: dict[str, Any] | None, markdown: str | None
    ) -> dict[str, Any]:
        if normalized_content is not None:
            content = dict(normalized_content)
            content.setdefault("title", title)
            return validate_normalized_artifact(content)
        if markdown is None:
            raise ValueError("normalized_content or markdown is required")
        return markdown_to_normalized(markdown, title=title)
