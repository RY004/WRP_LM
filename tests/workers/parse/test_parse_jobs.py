from saturn.documents.db_models import DocumentChunk, DocumentSection
from saturn.documents.service import DocumentService
from saturn.storage.filesystem import FilesystemStorage
from saturn.workers.jobs.parse import run_parse_job


def test_parse_job_materializes_sections_chunks_and_diagnostics_direct(
    phase2_session_factory, tmp_path
) -> None:
    session = phase2_session_factory()
    try:
        context, project_id = _seed_project(session)
        storage = FilesystemStorage(tmp_path)
        service = DocumentService(session, storage=storage)
        document = service.register_document(context, project_id, "Intake")
        session.flush()
        source, version, job = service.register_source_upload(
            context,
            document.id,
            "intake.md",
            "text/markdown",
            b"# Intake\n\nWelcome\n\n## Details\n\nMore text",
        )

        run_parse_job(session, storage, job.id)
        session.flush()

        assert version.parse_status == "parsed"
        sections = session.query(DocumentSection).filter_by(document_version_id=version.id).all()
        chunks = session.query(DocumentChunk).filter_by(document_version_id=version.id).all()
        assert [section.heading_path_text for section in sections] == [
            "Intake",
            "Intake > Details",
        ]
        assert sections[1].heading_path_ltree == "intake.details"
        assert chunks[0].section_id == sections[0].id
        assert storage.exists(source.storage_key)
    finally:
        session.close()


def _seed_project(session):
    from saturn.access.context import AuthContext
    from saturn.access.db_models import ProjectMembership
    from saturn.identity.db_models import Organization, User
    from saturn.projects.db_models import Project
    from saturn.shared.ids import new_id

    user = User(email=f"{new_id()}@example.com", display_name="Doc Owner")
    org = Organization(name="Docs Org", slug=new_id())
    session.add_all([user, org])
    session.flush()
    project = Project(org_id=org.id, name="Docs", slug=new_id(), created_by_user_id=user.id)
    session.add(project)
    session.flush()
    session.add(ProjectMembership(project_id=project.id, user_id=user.id, role="owner"))
    session.flush()
    return AuthContext(user_id=user.id, org_id=org.id), project.id
