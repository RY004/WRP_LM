"""Presence tracking service."""

from datetime import timedelta
from typing import Any

from sqlalchemy.orm import Session

from saturn.access.context import AuthContext
from saturn.access.policies import Permission, require_authenticated
from saturn.access.service import AccessService
from saturn.collaboration.db_models import PresenceMarker
from saturn.collaboration.repository import CollaborationRepository
from saturn.shared.time import utc_now


class PresenceService:
    def __init__(self, session: Session) -> None:
        self.repository = CollaborationRepository(session)
        self.access = AccessService(session)

    def upsert(
        self,
        context: AuthContext,
        project_id: str,
        stage: str,
        artifact_id: str | None = None,
        cursor: dict[str, Any] | None = None,
        ttl_seconds: int = 120,
    ) -> PresenceMarker:
        user_id = require_authenticated(context)
        self.access.require_project_permission(context, project_id, Permission.PROJECT_READ)
        marker = PresenceMarker(
            project_id=project_id,
            stage=stage,
            user_id=user_id,
            artifact_id=artifact_id,
            cursor=cursor,
            expires_at=utc_now() + timedelta(seconds=ttl_seconds),
        )
        return self.repository.upsert_presence(marker)

    def list(self, context: AuthContext, project_id: str, stage: str) -> list[PresenceMarker]:
        self.access.require_project_permission(context, project_id, Permission.PROJECT_READ)
        return self.repository.list_presence(project_id, stage)
