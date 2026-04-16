from fastapi.testclient import TestClient


def test_notion_oauth_resource_target_and_sync_trigger_flow(phase2_app) -> None:
    client = TestClient(phase2_app)
    token, project_id = _login(client)
    headers = {"X-Saturn-Session-Id": token}

    start = client.post("/api/v1/notion/oauth/start", headers=headers)
    assert start.status_code == 201
    state = start.json()["state"]
    assert "api.notion.com" in start.json()["authorization_url"]

    callback = client.post(
        "/api/v1/notion/oauth/callback",
        json={"code": "phase6", "state": state},
        headers=headers,
    )
    assert callback.status_code == 201
    account_id = callback.json()["id"]
    assert callback.json()["status"] == "active"

    resources = client.get(f"/api/v1/notion/accounts/{account_id}/resources", headers=headers)
    assert resources.status_code == 200
    assert resources.json()[0]["resource_type"] in {"page", "database"}

    target = client.post(
        "/api/v1/notion/targets",
        json={
            "account_id": account_id,
            "project_id": project_id,
            "notion_resource_id": "page-local-runbook",
            "resource_type": "page",
            "title": "Local Runbook",
        },
        headers=headers,
    )
    assert target.status_code == 201

    sync = client.post(f"/api/v1/notion/targets/{target.json()['id']}/sync", headers=headers)
    assert sync.status_code == 202
    assert sync.json()["queue_name"] == "notion_sync"
    assert sync.json()["status"] == "queued"


def _login(client: TestClient) -> tuple[str, str]:
    login = client.post(
        "/api/v1/auth/google/callback",
        json={"email": "phase6@example.com", "name": "Phase Six", "org_slug": "phase6-org"},
    )
    assert login.status_code == 200
    token = login.json()["session_id"]
    created = client.post(
        "/api/v1/projects",
        json={"name": "Phase 6 Project"},
        headers={"X-Saturn-Session-Id": token, "Idempotency-Key": "phase6-project"},
    )
    assert created.status_code == 201
    return token, created.json()["id"]
