"""Service layer for Notion integration."""

from datetime import timedelta

from sqlalchemy.orm import Session

from saturn.access.context import AuthContext
from saturn.access.policies import Permission, require_authenticated
from saturn.access.service import AccessService
from saturn.bootstrap.settings import Settings, get_settings
from saturn.documents.service import DocumentService
from saturn.embeddings.service import EmbeddingService
from saturn.integrations.notion.client import (
    LocalNotionClient,
    NotionClient,
    NotionMissingResource,
    NotionRateLimited,
    NotionUnauthorized,
)
from saturn.integrations.notion.db_models import (
    NotionAccount,
    NotionOAuthState,
    NotionSyncJob,
    NotionSyncTarget,
)
from saturn.integrations.notion.oauth import (
    build_authorization_url,
    new_oauth_state,
    protect_token,
    reveal_token,
)
from saturn.integrations.notion.repository import NotionRepository
from saturn.integrations.notion.resources import resource_to_read
from saturn.shared.time import utc_now
from saturn.storage.base import StorageBackend


class NotionService:
    def __init__(
        self,
        session: Session,
        settings: Settings | None = None,
        client: NotionClient | None = None,
        storage: StorageBackend | None = None,
    ) -> None:
        self.session = session
        self.settings = settings or get_settings()
        self.client = client or LocalNotionClient()
        self.storage = storage
        self.repository = NotionRepository(session)
        self.access = AccessService(session)

    def start_oauth(self, context: AuthContext):
        user_id = require_authenticated(context)
        if not context.org_id:
            raise PermissionError("Authentication required")
        state = new_oauth_state()
        self.repository.add(
            NotionOAuthState(state=state, user_id=user_id, org_id=context.org_id, status="pending")
        )
        return build_authorization_url(
            self.settings.notion_client_id,
            self.settings.notion_redirect_uri,
            state,
        ), state

    def complete_oauth(self, context: AuthContext, code: str, state_value: str) -> NotionAccount:
        user_id = require_authenticated(context)
        state = self.repository.get_state(state_value)
        if state is None or state.status != "pending" or state.user_id != user_id:
            raise PermissionError("Invalid Notion OAuth state")
        token = self.client.exchange_code(code)
        expires_at = (
            utc_now() + timedelta(seconds=token.expires_in_seconds)
            if token.expires_in_seconds
            else None
        )
        account = NotionAccount(
            org_id=state.org_id,
            owner_user_id=user_id,
            workspace_id=token.workspace_id,
            workspace_name=token.workspace_name,
            bot_id=token.bot_id,
            access_token_encrypted=protect_token(token.access_token),
            refresh_token_encrypted=protect_token(token.refresh_token) if token.refresh_token else None,
            token_expires_at=expires_at,
            status="active",
        )
        self.repository.add(account)
        state.status = "consumed"
        state.consumed_at = utc_now()
        return account

    def list_accounts(self, context: AuthContext) -> list[NotionAccount]:
        require_authenticated(context)
        if not context.org_id:
            raise PermissionError("Authentication required")
        return self.repository.list_accounts_for_org(context.org_id)

    def list_resources(self, context: AuthContext, account_id: str):
        account = self._account_for_user(context, account_id)
        try:
            return [resource_to_read(resource) for resource in self.client.list_resources(self._access_token(account))]
        except NotionUnauthorized as exc:
            self._mark_account_reconnect(account, str(exc))
            return []

    def create_target(
        self,
        context: AuthContext,
        account_id: str,
        project_id: str,
        notion_resource_id: str,
        resource_type: str,
        title: str,
    ) -> NotionSyncTarget:
        user_id = require_authenticated(context)
        self.access.require_project_permission(context, project_id, Permission.PROJECT_WRITE)
        self._account_for_user(context, account_id)
        target = NotionSyncTarget(
            account_id=account_id,
            project_id=project_id,
            notion_resource_id=notion_resource_id,
            resource_type=resource_type,
            title=title,
            created_by_user_id=user_id,
            status="active",
        )
        self.repository.add(target)
        self.session.flush()
        return target

    def list_targets(self, context: AuthContext, project_id: str) -> list[NotionSyncTarget]:
        self.access.require_project_permission(context, project_id, Permission.PROJECT_READ)
        return self.repository.list_targets_for_project(project_id)

    def trigger_sync(self, context: AuthContext, target_id: str) -> NotionSyncJob:
        target = self.repository.get_target(target_id)
        if target is None:
            raise LookupError("Notion sync target not found")
        self.access.require_project_permission(context, target.project_id, Permission.PROJECT_WRITE)
        job = NotionSyncJob(target_id=target.id, queue_name="notion_sync", status="queued")
        self.repository.add(job)
        self.session.flush()
        return job

    def run_sync_job(self, job_id: str) -> NotionSyncJob:
        if self.storage is None:
            raise ValueError("Storage backend is required for Notion sync")
        job = self.repository.get_job(job_id)
        if job is None:
            raise LookupError("Notion sync job not found")
        target = self.repository.get_target(job.target_id)
        if target is None:
            raise LookupError("Notion sync target not found")
        account = self.repository.get_account(target.account_id)
        if account is None:
            raise LookupError("Notion account not found")
        job.status = "running"
        job.attempts += 1
        try:
            content = self.client.fetch_content(
                self._access_token(account),
                target.notion_resource_id,
                cursor=target.cursor,
            )
        except NotionRateLimited as exc:
            job.status = "retry_scheduled"
            job.retry_after_seconds = exc.retry_after_seconds
            job.last_error = str(exc)
            target.status = "rate_limited"
            target.last_error = str(exc)
            return job
        except NotionUnauthorized as exc:
            self._mark_account_reconnect(account, str(exc))
            job.status = "blocked_reconnect"
            job.last_error = str(exc)
            target.status = "blocked_reconnect"
            target.last_error = str(exc)
            return job
        except NotionMissingResource as exc:
            job.status = "missing_resource"
            job.last_error = str(exc)
            target.status = "missing_resource"
            target.last_error = str(exc)
            return job

        context = AuthContext(user_id=account.owner_user_id, org_id=account.org_id)
        documents = DocumentService(self.session, storage=self.storage)
        if target.document_id:
            document = documents.get_document(context, target.document_id)
        else:
            document = documents.register_document(context, target.project_id, target.title, source_kind="notion")
            self.session.flush()
            target.document_id = document.id
        _source, _version, parse_job = documents.register_source_upload(
            context,
            document.id,
            filename=f"{target.notion_resource_id}.md",
            media_type="text/markdown",
            payload=content.markdown.encode("utf-8"),
        )
        embed_job = EmbeddingService(self.session).create_embed_job(context, target.project_id, "document_chunk")
        self.session.flush()
        target.title = content.resource.title
        target.cursor = content.cursor
        target.status = "active"
        target.last_error = None
        target.last_synced_at = utc_now()
        job.status = "queued_followup"
        job.queued_parse_job_id = parse_job.id
        job.queued_embed_job_id = embed_job.id
        job.diagnostics = {"pipeline": ["parse_job_queued", "embed_job_queued"]}
        job.last_error = None
        return job

    def _account_for_user(self, context: AuthContext, account_id: str) -> NotionAccount:
        user_id = require_authenticated(context)
        account = self.repository.get_account(account_id)
        if account is None:
            raise LookupError("Notion account not found")
        if account.owner_user_id != user_id and account.org_id != context.org_id:
            raise PermissionError("Insufficient Notion account access")
        return account

    def _access_token(self, account: NotionAccount) -> str:
        return reveal_token(account.access_token_encrypted)

    def _mark_account_reconnect(self, account: NotionAccount, reason: str) -> None:
        account.status = "reconnect_required"
        account.reconnect_reason = reason
