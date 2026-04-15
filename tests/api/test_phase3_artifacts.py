from fastapi.testclient import TestClient


def _login(client: TestClient, email: str) -> tuple[str, str]:
    login = client.post(
        "/api/v1/auth/google/callback",
        json={"email": email, "name": email.split("@")[0], "org_slug": "phase3-org"},
    )
    assert login.status_code == 200
    token = login.json()["session_id"]
    headers = {"X-Saturn-Session-Id": token, "Idempotency-Key": f"project-{email}"}
    created = client.post("/api/v1/projects", json={"name": f"Project {email}"}, headers=headers)
    assert created.status_code == 201
    return token, created.json()["id"]


def _session(client: TestClient, email: str) -> dict:
    login = client.post(
        "/api/v1/auth/google/callback",
        json={"email": email, "name": email.split("@")[0], "org_slug": "phase3-org"},
    )
    assert login.status_code == 200
    token = login.json()["session_id"]
    session = client.get("/api/v1/session", headers={"X-Saturn-Session-Id": token})
    assert session.status_code == 200
    return {"token": token, "user_id": session.json()["user"]["id"]}


def test_artifact_authoring_comments_presence_and_lock_flow(phase2_app) -> None:
    client = TestClient(phase2_app)
    token, project_id = _login(client, "owner3@example.com")
    headers = {"X-Saturn-Session-Id": token}

    created = client.post(
        "/api/v1/artifacts",
        json={"project_id": project_id, "title": "Phase 3 Plan", "markdown": "# Phase 3 Plan\n\nReady."},
        headers=headers,
    )
    assert created.status_code == 201
    artifact = created.json()
    assert artifact["current_version_number"] == 1
    assert artifact["index_projection"]["title"] == "Phase 3 Plan"

    updated = client.post(
        f"/api/v1/artifacts/{artifact['id']}/versions",
        json={
            "markdown": "# Phase 3 Plan\n\nReady.\n\n- API\n- Tests",
            "change_summary": "Add checklist",
        },
        headers=headers,
    )
    assert updated.status_code == 201
    assert updated.json()["version_number"] == 2

    comment = client.post(
        f"/api/v1/comments/artifacts/{artifact['id']}",
        json={"body": "Looks good"},
        headers=headers,
    )
    assert comment.status_code == 201
    edited = client.patch(
        f"/api/v1/comments/artifact-comments/{comment.json()['id']}",
        json={"body": "Looks very good"},
        headers=headers,
    )
    assert edited.status_code == 200
    assert edited.json()["body"] == "Looks very good"

    stage_comment = client.post(
        f"/api/v1/comments/projects/{project_id}/stages/implement",
        json={"body": "Implementation note"},
        headers=headers,
    )
    assert stage_comment.status_code == 201

    presence = client.put(
        f"/api/v1/comments/projects/{project_id}/stages/implement/presence",
        json={"artifact_id": artifact["id"], "cursor": {"block": 1}},
        headers=headers,
    )
    assert presence.status_code == 200
    assert presence.json()["cursor"] == {"block": 1}

    lock = client.post(
        f"/api/v1/comments/projects/{project_id}/stages/implement/lock",
        json={"artifact_id": artifact["id"]},
        headers=headers,
    )
    assert lock.status_code == 201
    locked_update = client.patch(
        f"/api/v1/artifacts/{artifact['id']}",
        json={"status": "review", "stage": "implement", "lock_token": lock.json()["token"]},
        headers=headers,
    )
    assert locked_update.status_code == 200
    assert locked_update.json()["status"] == "review"


def test_phase_lock_blocks_other_writer_but_not_comments(phase2_app) -> None:
    client = TestClient(phase2_app)
    owner_token, project_id = _login(client, "lock-owner@example.com")
    owner_headers = {"X-Saturn-Session-Id": owner_token}
    created = client.post(
        "/api/v1/artifacts",
        json={"project_id": project_id, "title": "Locked", "markdown": "# Locked\n"},
        headers=owner_headers,
    )
    assert created.status_code == 201
    artifact_id = created.json()["id"]

    lock = client.post(
        f"/api/v1/comments/projects/{project_id}/stages/implement/lock",
        json={"artifact_id": artifact_id},
        headers=owner_headers,
    )
    assert lock.status_code == 201

    other = _session(client, "lock-other@example.com")
    member = client.post(
        f"/api/v1/memberships/projects/{project_id}",
        json={"user_id": other["user_id"], "role": "member"},
        headers=owner_headers,
    )
    assert member.status_code == 201
    other_headers = {"X-Saturn-Session-Id": other["token"]}

    blocked = client.patch(
        f"/api/v1/artifacts/{artifact_id}",
        json={"status": "review", "stage": "implement"},
        headers=other_headers,
    )
    assert blocked.status_code == 403

    comment = client.post(
        f"/api/v1/comments/artifacts/{artifact_id}",
        json={"body": "Still allowed"},
        headers=other_headers,
    )
    assert comment.status_code == 201
