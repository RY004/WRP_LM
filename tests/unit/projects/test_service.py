from saturn.access.context import AuthContext
from saturn.identity.google_oauth import profile_from_test_callback
from saturn.identity.service import IdentityService
from saturn.pipeline.repository import PipelineRepository
from saturn.projects.service import ProjectService


def test_project_creation_adds_owner_membership_and_pipeline(phase2_session_factory) -> None:
    session = phase2_session_factory()
    user_session = IdentityService(session).oauth_login_test_mode(
        profile_from_test_callback("owner@example.com", "Owner"),
        org_name="Test Org",
        org_slug="test-org",
    )
    context = AuthContext(
        user_id=user_session.user_id,
        org_id=user_session.org_id,
        session_id=user_session.token,
    )

    project = ProjectService(session).create_project(context, "Alpha Project")
    session.commit()

    pipeline = PipelineRepository(session).get_by_project(project.id)
    members = ProjectService(session).list_members(context, project.id)
    assert project.slug == "alpha-project"
    assert pipeline is not None
    assert pipeline.current_stage == "question"
    assert [(member.user_id, member.role) for member in members] == [(user_session.user_id, "owner")]
