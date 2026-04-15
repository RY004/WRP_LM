"""Same-phase exclusivity service."""

from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session

from saturn.access.context import AuthContext
from saturn.access.policies import Permission, require_authenticated
from saturn.access.service import AccessService
from saturn.collaboration.db_models import PhaseLock
from saturn.collaboration.repository import CollaborationRepository
from saturn.shared.ids import new_id
from saturn.shared.time import utc_now


class PhaseLockService:
    def __init__(self, session: Session) -> None:
        self.repository = CollaborationRepository(session)
        self.access = AccessService(session)

    def acquire(
        self,
        context: AuthContext,
        project_id: str,
        stage: str,
        artifact_id: str | None = None,
        ttl_seconds: int = 900,
    ) -> PhaseLock:
        user_id = require_authenticated(context)
        self.access.require_project_permission(context, project_id, Permission.PROJECT_WRITE)
        self._delete_expired(project_id, stage)
        existing = self.repository.get_phase_lock(project_id, stage)
        expires_at = utc_now() + timedelta(seconds=ttl_seconds)
        if existing:
            if existing.holder_user_id != user_id:
                raise PermissionError("Phase is locked by another user")
            existing.artifact_id = artifact_id or existing.artifact_id
            existing.expires_at = expires_at
            return existing
        lock = PhaseLock(
            project_id=project_id,
            stage=stage,
            holder_user_id=user_id,
            artifact_id=artifact_id,
            token=new_id(),
            expires_at=expires_at,
        )
        self.repository.session.add(lock)
        return lock

    def release(self, context: AuthContext, project_id: str, stage: str, token: str) -> None:
        user_id = require_authenticated(context)
        lock = self.repository.get_phase_lock_by_token(token)
        if not lock or lock.project_id != project_id or lock.stage != stage:
            raise LookupError("Phase lock not found")
        if lock.holder_user_id != user_id:
            raise PermissionError("Only the lock holder can release the phase lock")
        self.repository.delete_phase_lock(lock)

    def require_writable(
        self, context: AuthContext, project_id: str, stage: str | None, token: str | None
    ) -> None:
        if stage is None:
            return
        user_id = require_authenticated(context)
        self._delete_expired(project_id, stage)
        lock = self.repository.get_phase_lock(project_id, stage)
        if lock is None:
            return
        if lock.holder_user_id == user_id and (token is None or token == lock.token):
            return
        raise PermissionError("Phase is locked by another user")

    def _delete_expired(self, project_id: str, stage: str) -> None:
        lock = self.repository.get_phase_lock(project_id, stage)
        if lock and _aware(lock.expires_at) <= utc_now():
            self.repository.delete_phase_lock(lock)


def _aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value
