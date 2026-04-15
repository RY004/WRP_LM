"""Base extensions migration scaffold."""

from alembic import op

revision = "0001_extensions_base"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS citext")
    op.execute("CREATE EXTENSION IF NOT EXISTS ltree")
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute(
        """
        CREATE OR REPLACE FUNCTION saturn_set_updated_at()
        RETURNS trigger AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
        """
    )


def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS saturn_set_updated_at()")
    op.execute("DROP EXTENSION IF EXISTS vector")
    op.execute("DROP EXTENSION IF EXISTS ltree")
    op.execute("DROP EXTENSION IF EXISTS citext")
