"""Repository layer for projects."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from saturn.projects.db_models import Project


class ProjectRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, org_id: str, name: str, slug: str, created_by_user_id: str) -> Project:
        project = Project(org_id=org_id, name=name, slug=slug, created_by_user_id=created_by_user_id)
        self.session.add(project)
        return project

    def get(self, project_id: str) -> Project | None:
        return self.session.get(Project, project_id)

    def list_for_org(self, org_id: str) -> list[Project]:
        return list(self.session.scalars(select(Project).where(Project.org_id == org_id)))
