"""Artifact routes."""

from fastapi import APIRouter

from saturn.api.deps import AuthContextDep, DbSessionDep
from saturn.artifacts.api_models import (
    ArtifactCreate,
    ArtifactMergeRequest,
    ArtifactRead,
    ArtifactUpdate,
    ArtifactVersionCreate,
    ArtifactVersionRead,
)
from saturn.artifacts.service import ArtifactService

router = APIRouter(prefix="/api/v1/artifacts", tags=["artifacts"])


@router.post("", response_model=ArtifactRead, status_code=201)
async def create_artifact(
    payload: ArtifactCreate, context: AuthContextDep, session: DbSessionDep
) -> ArtifactRead:
    artifact = ArtifactService(session).create_artifact(
        context,
        project_id=payload.project_id,
        title=payload.title,
        slug=payload.slug,
        artifact_type=payload.artifact_type,
        normalized_content=payload.normalized_content,
        markdown=payload.markdown,
        stage=payload.stage,
        lock_token=payload.lock_token,
    )
    session.commit()
    return ArtifactRead.model_validate(artifact)


@router.get("", response_model=list[ArtifactRead])
async def list_artifacts(
    project_id: str, context: AuthContextDep, session: DbSessionDep
) -> list[ArtifactRead]:
    return [
        ArtifactRead.model_validate(artifact)
        for artifact in ArtifactService(session).list_artifacts(context, project_id)
    ]


@router.get("/{artifact_id}", response_model=ArtifactRead)
async def get_artifact(
    artifact_id: str, context: AuthContextDep, session: DbSessionDep
) -> ArtifactRead:
    return ArtifactRead.model_validate(ArtifactService(session).get_artifact(context, artifact_id))


@router.patch("/{artifact_id}", response_model=ArtifactRead)
async def update_artifact(
    artifact_id: str, payload: ArtifactUpdate, context: AuthContextDep, session: DbSessionDep
) -> ArtifactRead:
    artifact = ArtifactService(session).update_artifact(
        context,
        artifact_id,
        title=payload.title,
        status=payload.status,
        normalized_content=payload.normalized_content,
        markdown=payload.markdown,
        change_summary=payload.change_summary,
        stage=payload.stage,
        lock_token=payload.lock_token,
    )
    session.commit()
    return ArtifactRead.model_validate(artifact)


@router.post("/{artifact_id}/versions", response_model=ArtifactVersionRead, status_code=201)
async def create_artifact_version(
    artifact_id: str, payload: ArtifactVersionCreate, context: AuthContextDep, session: DbSessionDep
) -> ArtifactVersionRead:
    version = ArtifactService(session).create_version(
        context,
        artifact_id,
        normalized_content=payload.normalized_content,
        markdown=payload.markdown,
        change_summary=payload.change_summary,
        stage=payload.stage,
        lock_token=payload.lock_token,
    )
    session.commit()
    return ArtifactVersionRead.model_validate(version)


@router.get("/{artifact_id}/versions", response_model=list[ArtifactVersionRead])
async def list_artifact_versions(
    artifact_id: str, context: AuthContextDep, session: DbSessionDep
) -> list[ArtifactVersionRead]:
    return [
        ArtifactVersionRead.model_validate(version)
        for version in ArtifactService(session).list_versions(context, artifact_id)
    ]


@router.get("/{artifact_id}/versions/{version_number}", response_model=ArtifactVersionRead)
async def get_artifact_version(
    artifact_id: str, version_number: int, context: AuthContextDep, session: DbSessionDep
) -> ArtifactVersionRead:
    return ArtifactVersionRead.model_validate(
        ArtifactService(session).get_version(context, artifact_id, version_number)
    )


@router.post("/merge")
async def merge_artifacts(
    payload: ArtifactMergeRequest, context: AuthContextDep, session: DbSessionDep
) -> dict:
    return ArtifactService(session).merge(context, payload.base, payload.left, payload.right)
