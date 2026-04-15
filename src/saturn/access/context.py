"""Authorization context resolution."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AuthContext:
    user_id: str | None
    org_id: str | None = None
    session_id: str | None = None

    @classmethod
    def anonymous(cls) -> "AuthContext":
        return cls(user_id=None)

    @property
    def is_authenticated(self) -> bool:
        return self.user_id is not None
