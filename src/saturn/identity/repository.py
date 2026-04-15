"""Repository layer for the identity domain."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from saturn.identity.db_models import GoogleIdentity, OrgMembership, Organization, User, UserSession


class IdentityRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_user(self, user_id: str) -> User | None:
        return self.session.get(User, user_id)

    def get_user_by_email(self, email: str) -> User | None:
        return self.session.scalar(select(User).where(User.email == email.lower()))

    def upsert_user(self, email: str, display_name: str | None = None) -> User:
        user = self.get_user_by_email(email)
        if user is None:
            user = User(email=email.lower(), display_name=display_name)
            self.session.add(user)
        elif display_name:
            user.display_name = display_name
        return user

    def get_or_create_organization(self, name: str, slug: str) -> Organization:
        org = self.session.scalar(select(Organization).where(Organization.slug == slug))
        if org is None:
            org = Organization(name=name, slug=slug)
            self.session.add(org)
        return org

    def add_org_membership(self, org_id: str, user_id: str, role: str) -> OrgMembership:
        membership = self.session.scalar(
            select(OrgMembership).where(
                OrgMembership.org_id == org_id, OrgMembership.user_id == user_id
            )
        )
        if membership is None:
            membership = OrgMembership(org_id=org_id, user_id=user_id, role=role)
            self.session.add(membership)
        else:
            membership.role = role
        return membership

    def link_google_identity(self, user_id: str, google_sub: str, email: str) -> GoogleIdentity:
        identity = self.session.scalar(
            select(GoogleIdentity).where(GoogleIdentity.google_sub == google_sub)
        )
        if identity is None:
            identity = GoogleIdentity(user_id=user_id, google_sub=google_sub, email=email.lower())
            self.session.add(identity)
        return identity

    def create_session(self, user_id: str, org_id: str, token: str) -> UserSession:
        session = UserSession(user_id=user_id, org_id=org_id, token=token)
        self.session.add(session)
        return session

    def get_session(self, token: str) -> UserSession | None:
        return self.session.scalar(select(UserSession).where(UserSession.token == token))
