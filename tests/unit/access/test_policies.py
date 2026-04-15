from saturn.access.context import AuthContext
from saturn.access.policies import Permission, role_allows


def test_role_permissions_are_deny_by_default() -> None:
    assert role_allows(None, Permission.PROJECT_READ) is False
    assert role_allows("viewer", Permission.PROJECT_WRITE) is False
    assert role_allows("owner", Permission.PIPELINE_APPROVE) is True


def test_auth_context_anonymous_is_not_authenticated() -> None:
    assert AuthContext.anonymous().is_authenticated is False
    assert AuthContext(user_id="user-1").is_authenticated is True
