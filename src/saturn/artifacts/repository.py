"""Repository layer for artifacts."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from saturn.artifacts.db_models import Artifact, ArtifactVersion


class ArtifactRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, artifact: Artifact) -> Artifact:
        self.session.add(artifact)
        return artifact

    def create_version(self, version: ArtifactVersion) -> ArtifactVersion:
        self.session.add(version)
        return version

    def get(self, artifact_id: str) -> Artifact | None:
        return self.session.get(Artifact, artifact_id)

    def list_for_project(self, project_id: str) -> list[Artifact]:
        return list(
            self.session.scalars(
                select(Artifact).where(Artifact.project_id == project_id).order_by(Artifact.updated_at.desc())
            )
        )

    def get_version(self, artifact_id: str, version_number: int) -> ArtifactVersion | None:
        return self.session.scalar(
            select(ArtifactVersion).where(
                ArtifactVersion.artifact_id == artifact_id,
                ArtifactVersion.version_number == version_number,
            )
        )

    def list_versions(self, artifact_id: str) -> list[ArtifactVersion]:
        return list(
            self.session.scalars(
                select(ArtifactVersion)
                .where(ArtifactVersion.artifact_id == artifact_id)
                .order_by(ArtifactVersion.version_number)
            )
        )
