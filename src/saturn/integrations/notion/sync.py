"""Notion sync orchestration helpers."""

from sqlalchemy.orm import Session

from saturn.integrations.notion.client import NotionClient
from saturn.integrations.notion.service import NotionService
from saturn.storage.base import StorageBackend


def run_notion_sync(
    session: Session,
    storage: StorageBackend,
    sync_job_id: str,
    client: NotionClient | None = None,
):
    return NotionService(session, client=client, storage=storage).run_sync_job(sync_job_id)
