import importlib


def test_0001_upgrade_creates_required_extensions(monkeypatch) -> None:
    migration = importlib.import_module("migrations.versions.0001_extensions_base")
    statements: list[str] = []

    class FakeOp:
        @staticmethod
        def execute(statement: str) -> None:
            statements.append(statement)

    monkeypatch.setattr(migration, "op", FakeOp)

    migration.upgrade()

    assert any("CREATE EXTENSION IF NOT EXISTS citext" in statement for statement in statements)
    assert any("CREATE EXTENSION IF NOT EXISTS ltree" in statement for statement in statements)
    assert any("CREATE EXTENSION IF NOT EXISTS vector" in statement for statement in statements)
    assert any("saturn_set_updated_at" in statement for statement in statements)
