import importlib


def test_0002_and_0003_create_phase2_tables(monkeypatch) -> None:
    created: list[str] = []

    class FakeOp:
        @staticmethod
        def create_table(name, *args, **kwargs):
            created.append(name)

        @staticmethod
        def create_index(*args, **kwargs):
            return None

    for module_name in (
        "migrations.versions.0002_identity_access",
        "migrations.versions.0003_projects_pipeline",
    ):
        migration = importlib.import_module(module_name)
        monkeypatch.setattr(migration, "op", FakeOp)
        migration.upgrade()

    assert {
        "users",
        "organizations",
        "org_memberships",
        "google_identities",
        "user_sessions",
        "projects",
        "project_memberships",
        "acl_grants",
        "pipeline_states",
        "pipeline_decisions",
        "pipeline_approvals",
    }.issubset(set(created))
