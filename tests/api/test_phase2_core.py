from fastapi.testclient import TestClient


def test_test_mode_oauth_session_project_and_pipeline_flow(phase2_app) -> None:
    client = TestClient(phase2_app)

    login = client.post(
        "/api/v1/auth/google/callback",
        json={"email": "owner@example.com", "name": "Owner", "org_slug": "test-org"},
    )
    assert login.status_code == 200
    token = login.json()["session_id"]
    headers = {"X-Saturn-Session-Id": token, "Idempotency-Key": "create-project-1"}

    session_response = client.get("/api/v1/session", headers=headers)
    assert session_response.status_code == 200
    assert session_response.json()["user"]["email"] == "owner@example.com"

    denied = client.post("/api/v1/projects", json={"name": "Denied"})
    assert denied.status_code == 401

    created = client.post("/api/v1/projects", json={"name": "Alpha Project"}, headers=headers)
    assert created.status_code == 201
    project_id = created.json()["id"]

    pipeline = client.get(f"/api/v1/pipeline/projects/{project_id}", headers=headers)
    assert pipeline.status_code == 200
    assert pipeline.json()["current_stage"] == "question"

    decision = client.post(
        f"/api/v1/pipeline/projects/{project_id}/decisions",
        json={"decision": "Proceed to research", "rationale": "Phase gate passed"},
        headers=headers,
    )
    assert decision.status_code == 201

    approved = client.post(
        f"/api/v1/pipeline/projects/{project_id}/approve",
        json={"note": "Approved"},
        headers=headers,
    )
    assert approved.status_code == 201

    advanced = client.post(
        f"/api/v1/pipeline/projects/{project_id}/advance",
        json={"override": False},
        headers=headers,
    )
    assert advanced.status_code == 200
    assert advanced.json()["current_stage"] == "research"

    handoff = client.get(f"/api/v1/pipeline/projects/{project_id}/handoff", headers=headers)
    assert handoff.status_code == 200
    assert handoff.json()["stage"] == "research"
    assert handoff.json()["next_stage"] == "structure"
