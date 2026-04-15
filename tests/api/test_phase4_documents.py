import base64

from fastapi.testclient import TestClient


def test_document_intake_upload_and_reindex_api_flow(phase2_app) -> None:
    client = TestClient(phase2_app)
    token, project_id = _login(client)
    headers = {"X-Saturn-Session-Id": token}

    created = client.post(
        "/api/v1/documents",
        json={"project_id": project_id, "title": "Research Brief"},
        headers=headers,
    )
    assert created.status_code == 201
    document = created.json()
    assert document["status"] == "registered"

    uploaded = client.post(
        f"/api/v1/documents/{document['id']}/sources",
        json={
            "filename": "brief.md",
            "media_type": "text/markdown",
            "content_base64": base64.b64encode(b"# Brief\n\nPhase 4").decode(),
        },
        headers=headers,
    )
    assert uploaded.status_code == 201
    payload = uploaded.json()
    assert payload["source"]["storage_key"].startswith(f"documents/{project_id}/")
    assert payload["version"]["parse_status"] == "pending"
    assert payload["parse_job"]["queue_name"] == "parse"
    assert payload["parse_job"]["status"] == "queued"

    versions = client.get(f"/api/v1/documents/{document['id']}/versions", headers=headers)
    assert versions.status_code == 200
    assert versions.json()[0]["version_number"] == 1

    reindex = client.post(
        f"/api/v1/documents/{document['id']}/reindex",
        json={"reason": "manual refresh"},
        headers=headers,
    )
    assert reindex.status_code == 202
    assert reindex.json()["status"] == "queued"


def _login(client: TestClient) -> tuple[str, str]:
    login = client.post(
        "/api/v1/auth/google/callback",
        json={"email": "phase4@example.com", "name": "Phase Four", "org_slug": "phase4-org"},
    )
    assert login.status_code == 200
    token = login.json()["session_id"]
    created = client.post(
        "/api/v1/projects",
        json={"name": "Phase 4 Project"},
        headers={"X-Saturn-Session-Id": token, "Idempotency-Key": "phase4-project"},
    )
    assert created.status_code == 201
    return token, created.json()["id"]
