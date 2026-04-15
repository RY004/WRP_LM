"""Service layer for projects."""

import re

from sqlalchemy.orm import Session

from saturn.access.context import AuthContext
from saturn.access.policies import Permission
from saturn.access.service import AccessService
from saturn.pipeline.repository import PipelineRepository
from saturn.projects.repository import ProjectRepository


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "project"


class ProjectService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = ProjectRepository(session)
        self.access = AccessService(session)
        self.pipeline_repository = PipelineRepository(session)

    def create_project(self, context: AuthContext, name: str, slug: str | None = None):
        if not context.user_id or not context.org_id:
            raise PermissionError("Authentication required")
        project = self.repository.create(
            org_id=context.org_id,
            name=name,
            slug=slug or slugify(name),
            created_by_user_id=context.user_id,
        )
        self.session.flush()
        self.access.add_project_member(project.id, context.user_id, "owner")
        self.pipeline_repository.create(project.id)
        self.session.flush()
        return project

    def get_project(self, context: AuthContext, project_id: str):
        self.access.require_project_permission(context, project_id, Permission.PROJECT_READ)
        return self.repository.get(project_id)

    def list_projects(self, context: AuthContext):
        if not context.org_id:
            raise PermissionError("Authentication required")
        return self.repository.list_for_org(context.org_id)

    def add_member(self, context: AuthContext, project_id: str, user_id: str, role: str):
        self.access.require_project_permission(context, project_id, Permission.PROJECT_ADMIN)
        return self.access.add_project_member(project_id, user_id, role)

    def list_members(self, context: AuthContext, project_id: str):
        self.access.require_project_permission(context, project_id, Permission.PROJECT_READ)
        return self.access.list_project_members(project_id)
