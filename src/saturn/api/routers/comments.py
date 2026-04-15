"""Comment, phase lock, and presence routes."""

from fastapi import APIRouter

from saturn.api.deps import AuthContextDep, DbSessionDep
from saturn.collaboration.api_models import (
    ArtifactCommentRead,
    CommentCreate,
    CommentUpdate,
    PhaseLockCreate,
    PhaseLockRead,
    PresenceRead,
    PresenceUpsert,
    StageCommentRead,
)
from saturn.collaboration.comments_service import CommentsService
from saturn.collaboration.phase_lock_service import PhaseLockService
from saturn.collaboration.presence_service import PresenceService

router = APIRouter(prefix="/api/v1/comments", tags=["comments"])


@router.post("/artifacts/{artifact_id}", response_model=ArtifactCommentRead, status_code=201)
async def create_artifact_comment(
    artifact_id: str, payload: CommentCreate, context: AuthContextDep, session: DbSessionDep
) -> ArtifactCommentRead:
    comment = CommentsService(session).create_artifact_comment(
        context, artifact_id, payload.body, payload.version_id
    )
    session.commit()
    return ArtifactCommentRead.model_validate(comment)


@router.get("/artifacts/{artifact_id}", response_model=list[ArtifactCommentRead])
async def list_artifact_comments(
    artifact_id: str, context: AuthContextDep, session: DbSessionDep
) -> list[ArtifactCommentRead]:
    return [
        ArtifactCommentRead.model_validate(comment)
        for comment in CommentsService(session).list_artifact_comments(context, artifact_id)
    ]


@router.patch("/artifact-comments/{comment_id}", response_model=ArtifactCommentRead)
async def update_artifact_comment(
    comment_id: str, payload: CommentUpdate, context: AuthContextDep, session: DbSessionDep
) -> ArtifactCommentRead:
    comment = CommentsService(session).update_artifact_comment(context, comment_id, payload.body)
    session.commit()
    return ArtifactCommentRead.model_validate(comment)


@router.delete("/artifact-comments/{comment_id}", status_code=204)
async def delete_artifact_comment(
    comment_id: str, context: AuthContextDep, session: DbSessionDep
) -> None:
    CommentsService(session).delete_artifact_comment(context, comment_id)
    session.commit()


@router.post("/projects/{project_id}/stages/{stage}", response_model=StageCommentRead, status_code=201)
async def create_stage_comment(
    project_id: str, stage: str, payload: CommentCreate, context: AuthContextDep, session: DbSessionDep
) -> StageCommentRead:
    comment = CommentsService(session).create_stage_comment(context, project_id, stage, payload.body)
    session.commit()
    return StageCommentRead.model_validate(comment)


@router.get("/projects/{project_id}/stages/{stage}", response_model=list[StageCommentRead])
async def list_stage_comments(
    project_id: str, stage: str, context: AuthContextDep, session: DbSessionDep
) -> list[StageCommentRead]:
    return [
        StageCommentRead.model_validate(comment)
        for comment in CommentsService(session).list_stage_comments(context, project_id, stage)
    ]


@router.patch("/stage-comments/{comment_id}", response_model=StageCommentRead)
async def update_stage_comment(
    comment_id: str, payload: CommentUpdate, context: AuthContextDep, session: DbSessionDep
) -> StageCommentRead:
    comment = CommentsService(session).update_stage_comment(context, comment_id, payload.body)
    session.commit()
    return StageCommentRead.model_validate(comment)


@router.delete("/stage-comments/{comment_id}", status_code=204)
async def delete_stage_comment(comment_id: str, context: AuthContextDep, session: DbSessionDep) -> None:
    CommentsService(session).delete_stage_comment(context, comment_id)
    session.commit()


@router.post("/projects/{project_id}/stages/{stage}/lock", response_model=PhaseLockRead, status_code=201)
async def acquire_phase_lock(
    project_id: str, stage: str, payload: PhaseLockCreate, context: AuthContextDep, session: DbSessionDep
) -> PhaseLockRead:
    lock = PhaseLockService(session).acquire(
        context, project_id, stage, artifact_id=payload.artifact_id, ttl_seconds=payload.ttl_seconds
    )
    session.commit()
    return PhaseLockRead.model_validate(lock)


@router.delete("/projects/{project_id}/stages/{stage}/lock/{token}", status_code=204)
async def release_phase_lock(
    project_id: str, stage: str, token: str, context: AuthContextDep, session: DbSessionDep
) -> None:
    PhaseLockService(session).release(context, project_id, stage, token)
    session.commit()


@router.put("/projects/{project_id}/stages/{stage}/presence", response_model=PresenceRead)
async def upsert_presence(
    project_id: str, stage: str, payload: PresenceUpsert, context: AuthContextDep, session: DbSessionDep
) -> PresenceRead:
    marker = PresenceService(session).upsert(
        context,
        project_id,
        stage,
        artifact_id=payload.artifact_id,
        cursor=payload.cursor,
        ttl_seconds=payload.ttl_seconds,
    )
    session.commit()
    return PresenceRead.model_validate(marker)


@router.get("/projects/{project_id}/stages/{stage}/presence", response_model=list[PresenceRead])
async def list_presence(
    project_id: str, stage: str, context: AuthContextDep, session: DbSessionDep
) -> list[PresenceRead]:
    return [
        PresenceRead.model_validate(marker)
        for marker in PresenceService(session).list(context, project_id, stage)
    ]
