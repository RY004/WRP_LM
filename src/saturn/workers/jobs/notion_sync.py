"""Notion sync worker job implementation."""

from sqlalchemy.orm import Session

from saturn.integrations.notion.client import NotionClient
from saturn.integrations.notion.sync import run_notion_sync
from saturn.storage.base import StorageBackend


def run_notion_sync_job(
    session: Session,
    storage: StorageBackend,
    sync_job_id: str,
    client: NotionClient | None = None,
):
    return run_notion_sync(session, storage, sync_job_id, client=client)
