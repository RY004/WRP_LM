"""Service layer for the identity domain."""

from sqlalchemy.orm import Session

from saturn.identity.db_models import UserSession
from saturn.identity.google_oauth import GoogleProfile
from saturn.identity.repository import IdentityRepository
from saturn.shared.ids import new_id


class IdentityService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = IdentityRepository(session)

    def oauth_login_test_mode(
        self, profile: GoogleProfile, org_name: str, org_slug: str
    ) -> UserSession:
        user = self.repository.upsert_user(profile.email, profile.display_name)
        self.session.flush()
        org = self.repository.get_or_create_organization(org_name, org_slug)
        self.session.flush()
        self.repository.add_org_membership(org.id, user.id, "owner")
        self.repository.link_google_identity(user.id, profile.sub, profile.email)
        token = new_id()
        user_session = self.repository.create_session(user.id, org.id, token)
        self.session.flush()
        return user_session

    def get_session(self, token: str) -> UserSession | None:
        return self.repository.get_session(token)

    def get_user(self, user_id: str):
        return self.repository.get_user(user_id)
