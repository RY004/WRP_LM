"""Repository layer for collaboration."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from saturn.collaboration.db_models import ArtifactComment, PhaseLock, PresenceMarker, StageComment
from saturn.shared.time import utc_now


class CollaborationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add_artifact_comment(self, comment: ArtifactComment) -> ArtifactComment:
        self.session.add(comment)
        return comment

    def add_stage_comment(self, comment: StageComment) -> StageComment:
        self.session.add(comment)
        return comment

    def get_artifact_comment(self, comment_id: str) -> ArtifactComment | None:
        return self.session.get(ArtifactComment, comment_id)

    def get_stage_comment(self, comment_id: str) -> StageComment | None:
        return self.session.get(StageComment, comment_id)

    def list_artifact_comments(self, artifact_id: str) -> list[ArtifactComment]:
        return list(
            self.session.scalars(
                select(ArtifactComment)
                .where(ArtifactComment.artifact_id == artifact_id, ArtifactComment.status == "active")
                .order_by(ArtifactComment.created_at)
            )
        )

    def list_stage_comments(self, project_id: str, stage: str) -> list[StageComment]:
        return list(
            self.session.scalars(
                select(StageComment)
                .where(
                    StageComment.project_id == project_id,
                    StageComment.stage == stage,
                    StageComment.status == "active",
                )
                .order_by(StageComment.created_at)
            )
        )

    def get_phase_lock(self, project_id: str, stage: str) -> PhaseLock | None:
        return self.session.scalar(
            select(PhaseLock).where(PhaseLock.project_id == project_id, PhaseLock.stage == stage)
        )

    def get_phase_lock_by_token(self, token: str) -> PhaseLock | None:
        return self.session.scalar(select(PhaseLock).where(PhaseLock.token == token))

    def delete_phase_lock(self, lock: PhaseLock) -> None:
        self.session.delete(lock)

    def upsert_presence(self, marker: PresenceMarker) -> PresenceMarker:
        existing = self.session.scalar(
            select(PresenceMarker).where(
                PresenceMarker.project_id == marker.project_id,
                PresenceMarker.stage == marker.stage,
                PresenceMarker.user_id == marker.user_id,
            )
        )
        if existing:
            existing.artifact_id = marker.artifact_id
            existing.cursor = marker.cursor
            existing.expires_at = marker.expires_at
            existing.updated_at = utc_now()
            return existing
        self.session.add(marker)
        return marker

    def list_presence(self, project_id: str, stage: str) -> list[PresenceMarker]:
        now = utc_now()
        return list(
            self.session.scalars(
                select(PresenceMarker).where(
                    PresenceMarker.project_id == project_id,
                    PresenceMarker.stage == stage,
                    PresenceMarker.expires_at > now,
                )
            )
        )
