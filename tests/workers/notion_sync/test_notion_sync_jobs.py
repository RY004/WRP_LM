from saturn.integrations.notion.client import (
    LocalNotionClient,
    NotionContent,
    NotionMissingResource,
    NotionRateLimited,
    NotionResource,
    NotionUnauthorized,
)
from saturn.integrations.notion.service import NotionService
from saturn.storage.filesystem import FilesystemStorage
from saturn.workers.jobs.notion_sync import run_notion_sync_job
from tests.workers.parse.test_parse_jobs import _seed_project


def test_notion_sync_queues_document_parse_and_embed_work(phase2_session_factory, tmp_path) -> None:
    session = phase2_session_factory()
    try:
        context, project_id = _seed_project(session)
        storage = FilesystemStorage(tmp_path)
        service = NotionService(session, client=FakeNotionClient(), storage=storage)
        account = _account(service, context)
        target = service.create_target(
            context,
            account.id,
            project_id,
            "notion-page",
            "page",
            "Notion Page",
        )
        job = service.trigger_sync(context, target.id)
        session.flush()

        run_notion_sync_job(session, storage, job.id, client=FakeNotionClient())
        session.flush()

        assert job.status == "queued_followup"
        assert job.queued_parse_job_id
        assert job.queued_embed_job_id
        assert target.document_id
        assert target.cursor == "cursor-v1"
        assert target.status == "active"
    finally:
        session.close()


def test_notion_sync_rate_limit_and_revocation_surface_state(phase2_session_factory, tmp_path) -> None:
    session = phase2_session_factory()
    try:
        context, project_id = _seed_project(session)
        storage = FilesystemStorage(tmp_path)
        service = NotionService(session, client=FakeNotionClient(mode="rate"), storage=storage)
        account = _account(service, context)
        target = service.create_target(context, account.id, project_id, "rate-limited", "page", "Rate")
        job = service.trigger_sync(context, target.id)
        session.flush()

        run_notion_sync_job(session, storage, job.id, client=FakeNotionClient(mode="rate"))
        assert job.status == "retry_scheduled"
        assert job.retry_after_seconds == 42
        assert target.status == "rate_limited"

        revoked_job = service.trigger_sync(context, target.id)
        session.flush()
        run_notion_sync_job(session, storage, revoked_job.id, client=FakeNotionClient(mode="unauthorized"))
        assert revoked_job.status == "blocked_reconnect"
        assert account.status == "reconnect_required"
    finally:
        session.close()


def _account(service: NotionService, context):
    _url, state = service.start_oauth(context)
    service.session.flush()
    account = service.complete_oauth(context, "ok", state)
    service.session.flush()
    return account


class FakeNotionClient(LocalNotionClient):
    def __init__(self, mode: str = "ok") -> None:
        self.mode = mode

    def fetch_content(self, access_token: str, resource_id: str, cursor: str | None = None) -> NotionContent:
        if self.mode == "rate":
            raise NotionRateLimited(42)
        if self.mode == "unauthorized":
            raise NotionUnauthorized("revoked")
        if self.mode == "missing":
            raise NotionMissingResource("gone")
        return NotionContent(
            resource=NotionResource(id=resource_id, resource_type="page", title="Synced Page"),
            markdown="# Synced Page\n\nHello from Notion.",
            cursor="cursor-v1",
        )
