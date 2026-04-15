"""Project membership routes."""

from fastapi import APIRouter

from saturn.api.deps import AuthContextDep, DbSessionDep
from saturn.projects.api_models import ProjectMemberAdd, ProjectMemberRead
from saturn.projects.service import ProjectService

router = APIRouter(prefix="/api/v1/memberships", tags=["memberships"])


@router.get("/projects/{project_id}", response_model=list[ProjectMemberRead])
async def list_project_members(
    project_id: str, context: AuthContextDep, session: DbSessionDep
) -> list[ProjectMemberRead]:
    return [
        ProjectMemberRead.model_validate(member)
        for member in ProjectService(session).list_members(context, project_id)
    ]


@router.post("/projects/{project_id}", response_model=ProjectMemberRead, status_code=201)
async def add_project_member(
    project_id: str, payload: ProjectMemberAdd, context: AuthContextDep, session: DbSessionDep
) -> ProjectMemberRead:
    member = ProjectService(session).add_member(context, project_id, payload.user_id, payload.role)
    session.commit()
    return ProjectMemberRead.model_validate(member)
