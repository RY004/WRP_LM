"""Authorization policy helpers."""

from enum import StrEnum

from saturn.access.context import AuthContext


class Role(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class Permission(StrEnum):
    PROJECT_READ = "project:read"
    PROJECT_WRITE = "project:write"
    PROJECT_ADMIN = "project:admin"
    PIPELINE_READ = "pipeline:read"
    PIPELINE_ADVANCE = "pipeline:advance"
    PIPELINE_APPROVE = "pipeline:approve"


ROLE_PERMISSIONS: dict[str, set[str]] = {
    Role.OWNER: {permission.value for permission in Permission},
    Role.ADMIN: {permission.value for permission in Permission},
    Role.MEMBER: {
        Permission.PROJECT_READ,
        Permission.PROJECT_WRITE,
        Permission.PIPELINE_READ,
        Permission.PIPELINE_ADVANCE,
    },
    Role.VIEWER: {Permission.PROJECT_READ, Permission.PIPELINE_READ},
}


def role_allows(role: str | None, permission: str | Permission) -> bool:
    if role is None:
        return False
    value = permission.value if isinstance(permission, Permission) else permission
    allowed = ROLE_PERMISSIONS.get(role, set())
    return value in {item.value if isinstance(item, Permission) else item for item in allowed}


def require_authenticated(context: AuthContext) -> str:
    if not context.user_id:
        raise PermissionError("Authentication required")
    return context.user_id
