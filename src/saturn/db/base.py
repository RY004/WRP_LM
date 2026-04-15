"""SQLAlchemy declarative base."""

from sqlalchemy.orm import DeclarativeBase

from saturn.db.metadata import metadata


class Base(DeclarativeBase):
    """Base model for all DB entities."""

    metadata = metadata
