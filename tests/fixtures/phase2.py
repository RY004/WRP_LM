from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from saturn.access.db_models import AclGrant, ProjectMembership
from saturn.api.app import create_app
from saturn.artifacts.db_models import Artifact, ArtifactVersion
from saturn.bootstrap.settings import Settings
from saturn.collaboration.db_models import ArtifactComment, PhaseLock, PresenceMarker, StageComment
from saturn.db.base import Base
from saturn.documents.db_models import (
    Document,
    DocumentChunk,
    DocumentParseJob,
    DocumentReindexRequest,
    DocumentSection,
    DocumentSource,
    DocumentVersion,
    ParseDiagnostic,
)
from saturn.identity.db_models import GoogleIdentity, OrgMembership, Organization, User, UserSession
from saturn.pipeline.db_models import PipelineApproval, PipelineDecision, PipelineState
from saturn.projects.db_models import Project

_MODELS = (
    User,
    Organization,
    OrgMembership,
    GoogleIdentity,
    UserSession,
    Project,
    ProjectMembership,
    AclGrant,
    PipelineState,
    PipelineDecision,
    PipelineApproval,
    Artifact,
    ArtifactVersion,
    ArtifactComment,
    StageComment,
    PresenceMarker,
    PhaseLock,
    Document,
    DocumentSource,
    DocumentVersion,
    DocumentSection,
    DocumentChunk,
    ParseDiagnostic,
    DocumentParseJob,
    DocumentReindexRequest,
)


@pytest.fixture()
def phase2_session_factory(tmp_path) -> Iterator[sessionmaker[Session]]:
    engine = create_engine(f"sqlite+pysqlite:///{tmp_path / 'phase2.db'}", future=True)
    Base.metadata.create_all(engine)
    yield sessionmaker(bind=engine, expire_on_commit=False)
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def phase2_app(phase2_session_factory):
    app = create_app(Settings(app_env="test", database_url="sqlite+pysqlite:///:memory:"))
    app.state.container.set_session_factory(phase2_session_factory)
    return app
