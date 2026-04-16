"""Repository layer for Notion integration."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from saturn.integrations.notion.db_models import (
    NotionAccount,
    NotionOAuthState,
    NotionSyncJob,
    NotionSyncTarget,
)


class NotionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, model):
        self.session.add(model)
        return model

    def get_state(self, state: str) -> NotionOAuthState | None:
        return self.session.scalar(select(NotionOAuthState).where(NotionOAuthState.state == state))

    def get_account(self, account_id: str) -> NotionAccount | None:
        return self.session.get(NotionAccount, account_id)

    def list_accounts_for_org(self, org_id: str) -> list[NotionAccount]:
        return list(self.session.scalars(select(NotionAccount).where(NotionAccount.org_id == org_id)))

    def get_target(self, target_id: str) -> NotionSyncTarget | None:
        return self.session.get(NotionSyncTarget, target_id)

    def list_targets_for_project(self, project_id: str) -> list[NotionSyncTarget]:
        return list(
            self.session.scalars(
                select(NotionSyncTarget).where(NotionSyncTarget.project_id == project_id)
            )
        )

    def get_job(self, job_id: str) -> NotionSyncJob | None:
        return self.session.get(NotionSyncJob, job_id)
