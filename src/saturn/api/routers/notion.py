"""Notion integration routes."""

from fastapi import APIRouter

from saturn.api.deps import AuthContextDep, DbSessionDep, SettingsDep, StorageDep
from saturn.integrations.notion.api_models import (
    NotionAccountRead,
    NotionOAuthCallback,
    NotionOAuthStartRead,
    NotionResourceRead,
    NotionSyncJobRead,
    NotionSyncTargetCreate,
    NotionSyncTargetRead,
)
from saturn.integrations.notion.service import NotionService

router = APIRouter(prefix="/api/v1/notion", tags=["notion"])


@router.post("/oauth/start", response_model=NotionOAuthStartRead, status_code=201)
async def start_oauth(
    context: AuthContextDep, session: DbSessionDep, settings: SettingsDep
) -> NotionOAuthStartRead:
    authorization_url, state = NotionService(session, settings=settings).start_oauth(context)
    session.commit()
    return NotionOAuthStartRead(authorization_url=authorization_url, state=state)


@router.post("/oauth/callback", response_model=NotionAccountRead, status_code=201)
async def complete_oauth(
    payload: NotionOAuthCallback,
    context: AuthContextDep,
    session: DbSessionDep,
    settings: SettingsDep,
) -> NotionAccountRead:
    account = NotionService(session, settings=settings).complete_oauth(
        context,
        code=payload.code,
        state_value=payload.state,
    )
    session.commit()
    return NotionAccountRead.model_validate(account)


@router.get("/accounts", response_model=list[NotionAccountRead])
async def list_accounts(context: AuthContextDep, session: DbSessionDep) -> list[NotionAccountRead]:
    return [NotionAccountRead.model_validate(account) for account in NotionService(session).list_accounts(context)]


@router.get("/accounts/{account_id}/resources", response_model=list[NotionResourceRead])
async def list_resources(
    account_id: str, context: AuthContextDep, session: DbSessionDep
) -> list[NotionResourceRead]:
    return NotionService(session).list_resources(context, account_id)


@router.post("/targets", response_model=NotionSyncTargetRead, status_code=201)
async def create_target(
    payload: NotionSyncTargetCreate,
    context: AuthContextDep,
    session: DbSessionDep,
) -> NotionSyncTargetRead:
    target = NotionService(session).create_target(
        context,
        account_id=payload.account_id,
        project_id=payload.project_id,
        notion_resource_id=payload.notion_resource_id,
        resource_type=payload.resource_type,
        title=payload.title,
    )
    session.commit()
    return NotionSyncTargetRead.model_validate(target)


@router.get("/projects/{project_id}/targets", response_model=list[NotionSyncTargetRead])
async def list_targets(
    project_id: str, context: AuthContextDep, session: DbSessionDep
) -> list[NotionSyncTargetRead]:
    return [
        NotionSyncTargetRead.model_validate(target)
        for target in NotionService(session).list_targets(context, project_id)
    ]


@router.post("/targets/{target_id}/sync", response_model=NotionSyncJobRead, status_code=202)
async def trigger_sync(
    target_id: str,
    context: AuthContextDep,
    session: DbSessionDep,
    storage: StorageDep,
) -> NotionSyncJobRead:
    job = NotionService(session, storage=storage).trigger_sync(context, target_id)
    session.commit()
    return NotionSyncJobRead.model_validate(job)
