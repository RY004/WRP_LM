"""Project routes."""

from fastapi import APIRouter

from saturn.api.deps import AuthContextDep, DbSessionDep
from saturn.projects.api_models import ProjectCreate, ProjectRead
from saturn.projects.service import ProjectService

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])


@router.post("", response_model=ProjectRead, status_code=201)
async def create_project(
    payload: ProjectCreate, context: AuthContextDep, session: DbSessionDep
) -> ProjectRead:
    project = ProjectService(session).create_project(context, payload.name, payload.slug)
    session.commit()
    return ProjectRead.model_validate(project)


@router.get("", response_model=list[ProjectRead])
async def list_projects(context: AuthContextDep, session: DbSessionDep) -> list[ProjectRead]:
    return [ProjectRead.model_validate(project) for project in ProjectService(session).list_projects(context)]


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: str, context: AuthContextDep, session: DbSessionDep
) -> ProjectRead:
    project = ProjectService(session).get_project(context, project_id)
    if project is None:
        raise LookupError("Project not found")
    return ProjectRead.model_validate(project)
