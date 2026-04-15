"""Service layer for the access domain."""

from sqlalchemy.orm import Session

from saturn.access.context import AuthContext
from saturn.access.policies import Permission, role_allows
from saturn.access.repository import AccessRepository


class AccessService:
    def __init__(self, session: Session) -> None:
        self.repository = AccessRepository(session)

    def require_project_permission(
        self, context: AuthContext, project_id: str, permission: Permission | str
    ) -> None:
        if not context.user_id:
            raise PermissionError("Authentication required")
        if self.can(context, project_id, permission):
            return
        raise PermissionError("Insufficient project access")

    def can(self, context: AuthContext, project_id: str, permission: Permission | str) -> bool:
        if not context.user_id:
            return False
        value = permission.value if isinstance(permission, Permission) else permission
        membership = self.repository.get_project_membership(project_id, context.user_id)
        if membership and role_allows(membership.role, value):
            return True
        return self.repository.has_grant(project_id, context.user_id, value)

    def add_project_member(self, project_id: str, user_id: str, role: str):
        return self.repository.add_project_membership(project_id, user_id, role)

    def list_project_members(self, project_id: str):
        return self.repository.list_project_memberships(project_id)
