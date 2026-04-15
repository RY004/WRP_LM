"""Repository layer for the access domain."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from saturn.access.db_models import AclGrant, ProjectMembership


class AccessRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add_project_membership(self, project_id: str, user_id: str, role: str) -> ProjectMembership:
        membership = self.get_project_membership(project_id, user_id)
        if membership is not None:
            membership.role = role
            return membership
        membership = ProjectMembership(project_id=project_id, user_id=user_id, role=role)
        self.session.add(membership)
        return membership

    def get_project_membership(self, project_id: str, user_id: str) -> ProjectMembership | None:
        return self.session.scalar(
            select(ProjectMembership).where(
                ProjectMembership.project_id == project_id,
                ProjectMembership.user_id == user_id,
            )
        )

    def list_project_memberships(self, project_id: str) -> list[ProjectMembership]:
        return list(
            self.session.scalars(
                select(ProjectMembership).where(ProjectMembership.project_id == project_id)
            )
        )

    def grant(self, project_id: str, user_id: str, permission: str) -> AclGrant:
        existing = self.session.scalar(
            select(AclGrant).where(
                AclGrant.project_id == project_id,
                AclGrant.user_id == user_id,
                AclGrant.permission == permission,
            )
        )
        if existing is not None:
            return existing
        grant = AclGrant(project_id=project_id, user_id=user_id, permission=permission)
        self.session.add(grant)
        return grant

    def has_grant(self, project_id: str, user_id: str, permission: str) -> bool:
        return (
            self.session.scalar(
                select(AclGrant.id).where(
                    AclGrant.project_id == project_id,
                    AclGrant.user_id == user_id,
                    AclGrant.permission == permission,
                )
            )
            is not None
        )
