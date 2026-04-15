"""Database engine and session scaffold."""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from cortex.bootstrap.settings import get_settings


def create_session_factory() -> sessionmaker[Session]:
    settings = get_settings()
    engine = create_engine(settings.database_url, future=True)
    return sessionmaker(bind=engine, expire_on_commit=False)
