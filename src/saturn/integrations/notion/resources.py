"""Notion resource mapping."""

from saturn.integrations.notion.api_models import NotionResourceRead
from saturn.integrations.notion.client import NotionResource


def resource_to_read(resource: NotionResource) -> NotionResourceRead:
    return NotionResourceRead(
        id=resource.id,
        resource_type=resource.resource_type,
        title=resource.title,
        updated_cursor=resource.updated_cursor,
    )
