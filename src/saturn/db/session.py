"""Database engine and session wiring."""

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from saturn.bootstrap.settings import Settings, get_settings


def create_db_engine(settings: Settings | None = None) -> Engine:
    settings = settings or get_settings()
    return create_engine(
        settings.database_url,
        echo=settings.database_echo,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        future=True,
    )


def create_session_factory(
    settings: Settings | None = None, engine: Engine | None = None
) -> sessionmaker[Session]:
    engine = engine or create_db_engine(settings)
    return sessionmaker(bind=engine, expire_on_commit=False)


@contextmanager
def session_scope(factory: sessionmaker[Session] | None = None) -> Iterator[Session]:
    session_factory = factory or create_session_factory()
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
