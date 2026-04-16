from fastapi.testclient import TestClient


def test_plugin_registry_install_execute_and_capability_gating(phase2_app) -> None:
    client = TestClient(phase2_app)
    token, project_id = _login(client)
    headers = {"X-Saturn-Session-Id": token}

    registered = client.post(
        "/api/v1/plugins",
        headers=headers,
        json={
            "key": "saturn-core",
            "name": "Saturn Core",
            "version": "1.0.0",
            "capabilities": [
                {"capability": "pipeline.get", "domain": "pipeline"},
                {"capability": "rag.query", "domain": "rag"},
            ],
        },
    )
    assert registered.status_code == 201

    installed = client.post(
        "/api/v1/plugins/installations",
        headers=headers,
        json={
            "plugin_key": "saturn-core",
            "version": "1.0.0",
            "project_id": project_id,
            "enabled": True,
        },
    )
    assert installed.status_code == 201
    assert installed.json()["enabled"] is True

    executed = client.post(
        "/api/v1/plugins/execute",
        headers=headers,
        json={
            "plugin_key": "saturn-core",
            "project_id": project_id,
            "capability": "pipeline.get",
            "input": {},
        },
    )
    assert executed.status_code == 200
    assert executed.json()["status"] == "succeeded"
    assert executed.json()["result"]["project_id"] == project_id

    blocked = client.post(
        "/api/v1/plugins/execute",
        headers=headers,
        json={
            "plugin_key": "saturn-core",
            "project_id": project_id,
            "capability": "wiki.create",
            "input": {"title": "Nope", "markdown": "# Nope"},
        },
    )
    assert blocked.status_code == 403


def test_vscode_token_exchange_and_workspace_session(phase2_app) -> None:
    client = TestClient(phase2_app)
    token, project_id = _login(client, email="phase7-vscode@example.com")

    exchange = client.post(
        "/api/v1/plugins/vscode/token-exchanges",
        json={"session_token": token},
    )
    assert exchange.status_code == 201

    session = client.post(
        "/api/v1/plugins/vscode/workspace-sessions",
        json={
            "exchange_token": exchange.json()["exchange_token"],
            "project_id": project_id,
            "workspace_uri": "file:///workspaces/WRP_LM",
            "agent_id": "codex",
        },
    )
    assert session.status_code == 201
    assert session.json()["project_id"] == project_id
    assert "rag.query" in session.json()["capabilities"]


def _login(
    client: TestClient,
    email: str = "phase7@example.com",
    project_name: str = "Phase 7 Project",
) -> tuple[str, str]:
    login = client.post(
        "/api/v1/auth/google/callback",
        json={"email": email, "name": "Phase Seven", "org_slug": email.split("@")[0]},
    )
    assert login.status_code == 200
    token = login.json()["session_id"]
    created = client.post(
        "/api/v1/projects",
        json={"name": project_name},
        headers={"X-Saturn-Session-Id": token, "Idempotency-Key": project_name},
    )
    assert created.status_code == 201
    return token, created.json()["id"]
