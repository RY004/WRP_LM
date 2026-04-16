"""Notion client contracts and local HTTP-free implementation."""

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from saturn.integrations.notion.oauth import NotionTokenPayload


class NotionRateLimited(Exception):
    def __init__(self, retry_after_seconds: int) -> None:
        super().__init__("Notion rate limit")
        self.retry_after_seconds = retry_after_seconds


class NotionUnauthorized(Exception):
    pass


class NotionMissingResource(Exception):
    pass


@dataclass(frozen=True, slots=True)
class NotionResource:
    id: str
    resource_type: str
    title: str
    updated_cursor: str | None = None


@dataclass(frozen=True, slots=True)
class NotionContent:
    resource: NotionResource
    markdown: str
    cursor: str


@runtime_checkable
class NotionClient(Protocol):
    def exchange_code(self, code: str) -> NotionTokenPayload: ...

    def list_resources(self, access_token: str) -> list[NotionResource]: ...

    def fetch_content(self, access_token: str, resource_id: str, cursor: str | None = None) -> NotionContent: ...


class LocalNotionClient:
    def exchange_code(self, code: str) -> NotionTokenPayload:
        if code == "revoked":
            raise NotionUnauthorized("Notion OAuth code was rejected")
        return NotionTokenPayload(
            access_token=f"notion-access-{code}",
            refresh_token=f"notion-refresh-{code}",
            workspace_id="workspace-local",
            workspace_name="Local Notion",
            bot_id="bot-local",
        )

    def list_resources(self, access_token: str) -> list[NotionResource]:
        self._raise_for_token(access_token)
        return [
            NotionResource(id="page-local-runbook", resource_type="page", title="Local Runbook"),
            NotionResource(id="database-local-roadmap", resource_type="database", title="Local Roadmap"),
        ]

    def fetch_content(self, access_token: str, resource_id: str, cursor: str | None = None) -> NotionContent:
        self._raise_for_token(access_token)
        if resource_id == "missing":
            raise NotionMissingResource("Notion resource is no longer accessible")
        if resource_id == "rate-limited":
            raise NotionRateLimited(30)
        resource = NotionResource(
            id=resource_id,
            resource_type="database" if "database" in resource_id else "page",
            title=resource_id.replace("-", " ").title(),
        )
        next_cursor = f"{resource_id}:v2" if cursor else f"{resource_id}:v1"
        markdown = f"# {resource.title}\n\nSynced from Notion resource `{resource_id}`.\n"
        return NotionContent(resource=resource, markdown=markdown, cursor=next_cursor)

    def _raise_for_token(self, access_token: str) -> None:
        if "revoked" in access_token or "expired" in access_token:
            raise NotionUnauthorized("Notion token is revoked or expired")
