"""Plugin gateway and bridge routes."""

from fastapi import APIRouter

from saturn.agents.vscode.token_exchange import VSCodeTokenExchangeService
from saturn.agents.vscode.workspace_sessions import VSCodeWorkspaceSessionService
from saturn.api.deps import AuthContextDep, DbSessionDep
from saturn.plugins.api_models import (
    EgressPolicyCreate,
    PluginEnableRequest,
    PluginExecuteRequest,
    PluginExecuteResponse,
    PluginInstallRequest,
    PluginInstallationRead,
    PluginRead,
    PluginRegisterRequest,
    PluginVersionRead,
    VSCodeTokenExchangeRequest,
    VSCodeTokenExchangeResponse,
    VSCodeWorkspaceSessionRead,
    VSCodeWorkspaceSessionRequest,
)
from saturn.plugins.egress.policies import PluginEgressPolicyService
from saturn.plugins.gateway import PluginGateway
from saturn.plugins.registry import PluginRegistryService

router = APIRouter(prefix="/api/v1/plugins", tags=["plugins"])


@router.post("", status_code=201)
async def register_plugin(
    payload: PluginRegisterRequest, context: AuthContextDep, session: DbSessionDep
) -> dict[str, object]:
    plugin, version = PluginRegistryService(session).register(
        context,
        key=payload.key,
        name=payload.name,
        description=payload.description,
        version=payload.version,
        entrypoint=payload.entrypoint,
        manifest=payload.manifest,
        capabilities=payload.capabilities,
    )
    session.commit()
    return {
        "plugin": PluginRead.model_validate(plugin).model_dump(),
        "version": PluginVersionRead.model_validate(version).model_dump(),
    }


@router.get("", response_model=list[PluginRead])
async def list_plugins(session: DbSessionDep) -> list[PluginRead]:
    return [PluginRead.model_validate(row) for row in PluginRegistryService(session).list_plugins()]


@router.post("/installations", response_model=PluginInstallationRead, status_code=201)
async def install_plugin(
    payload: PluginInstallRequest, context: AuthContextDep, session: DbSessionDep
) -> PluginInstallationRead:
    row = PluginRegistryService(session).install(
        context,
        plugin_key=payload.plugin_key,
        version=payload.version,
        project_id=payload.project_id,
        enabled=payload.enabled,
    )
    session.commit()
    return PluginInstallationRead.model_validate(row)


@router.get("/installations", response_model=list[PluginInstallationRead])
async def list_installations(
    context: AuthContextDep, session: DbSessionDep, project_id: str | None = None
) -> list[PluginInstallationRead]:
    return [
        PluginInstallationRead.model_validate(row)
        for row in PluginRegistryService(session).list_installations(context, project_id)
    ]


@router.patch("/installations/{installation_id}", response_model=PluginInstallationRead)
async def enable_installation(
    installation_id: str,
    payload: PluginEnableRequest,
    context: AuthContextDep,
    session: DbSessionDep,
) -> PluginInstallationRead:
    row = PluginRegistryService(session).set_enabled(context, installation_id, payload.enabled)
    session.commit()
    return PluginInstallationRead.model_validate(row)


@router.post("/execute", response_model=PluginExecuteResponse)
async def execute_plugin(
    payload: PluginExecuteRequest, context: AuthContextDep, session: DbSessionDep
) -> PluginExecuteResponse:
    execution, result = PluginGateway(session).execute(
        context,
        plugin_key=payload.plugin_key,
        project_id=payload.project_id,
        capability=payload.capability,
        payload=payload.input,
    )
    session.commit()
    return PluginExecuteResponse(execution_id=execution.id, status=execution.status, result=result)


@router.post("/egress/policies", status_code=201)
async def create_egress_policy(
    payload: EgressPolicyCreate, context: AuthContextDep, session: DbSessionDep
) -> dict[str, str]:
    row = PluginEgressPolicyService(session).create_policy(
        context,
        plugin_key=payload.plugin_key,
        project_id=payload.project_id,
        scheme=payload.scheme,
        host=payload.host,
        methods=payload.methods,
    )
    session.commit()
    return {"id": row.id}


@router.post("/vscode/token-exchanges", response_model=VSCodeTokenExchangeResponse, status_code=201)
async def create_vscode_token_exchange(
    payload: VSCodeTokenExchangeRequest, session: DbSessionDep
) -> VSCodeTokenExchangeResponse:
    row = VSCodeTokenExchangeService(session).create_exchange(payload.session_token)
    session.commit()
    return VSCodeTokenExchangeResponse(exchange_token=row.exchange_token, status=row.status)


@router.post(
    "/vscode/workspace-sessions", response_model=VSCodeWorkspaceSessionRead, status_code=201
)
async def create_vscode_workspace_session(
    payload: VSCodeWorkspaceSessionRequest, session: DbSessionDep
) -> VSCodeWorkspaceSessionRead:
    row = VSCodeWorkspaceSessionService(session).create_or_get(
        payload.exchange_token,
        project_id=payload.project_id,
        workspace_uri=payload.workspace_uri,
        agent_id=payload.agent_id,
    )
    session.commit()
    return VSCodeWorkspaceSessionRead.model_validate(row)
