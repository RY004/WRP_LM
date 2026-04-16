import base64

from fastapi.testclient import TestClient

from saturn.embeddings.service import EmbeddingService
from saturn.workers.jobs.embed import run_embed_job
from saturn.workers.jobs.parse import run_parse_job


def test_retrieval_api_degraded_and_hybrid_modes(phase2_app) -> None:
    client = TestClient(phase2_app)
    token, project_id = _login(client)
    headers = {"X-Saturn-Session-Id": token}
    document_id, parse_job_id = _upload_document(client, headers, project_id)

    with phase2_app.state.container.session_factory() as session:
        storage = phase2_app.state.container.storage
        run_parse_job(session, storage, parse_job_id)
        session.commit()

    degraded = client.post(
        "/api/v1/retrieval/query",
        json={
            "project_id": project_id,
            "query": "billing retry",
            "mode": "strict_section",
            "section_path_prefix": "Operations",
            "include_artifacts": False,
        },
        headers=headers,
    )
    assert degraded.status_code == 200
    degraded_payload = degraded.json()
    assert degraded_payload["degraded"] is True
    assert degraded_payload["results"][0]["citation"]["heading_path_text"].startswith("Operations")

    with phase2_app.state.container.session_factory() as session:
        job = EmbeddingService(session).create_embed_job(_context_for_token(session, token), project_id)
        session.flush()
        run_embed_job(session, job.id)
        session.commit()

    hybrid = client.post(
        "/api/v1/retrieval/query",
        json={
            "project_id": project_id,
            "query": "billing retry",
            "mode": "heading_boosted",
            "include_artifacts": False,
        },
        headers=headers,
    )
    assert hybrid.status_code == 200
    hybrid_payload = hybrid.json()
    assert hybrid_payload["degraded"] is False
    assert hybrid_payload["results"][0]["vector_score"] is not None
    assert hybrid_payload["results"][0]["confidence"] in {"low", "medium", "high"}
    assert document_id


def _login(client: TestClient) -> tuple[str, str]:
    login = client.post(
        "/api/v1/auth/google/callback",
        json={"email": "phase5@example.com", "name": "Phase Five", "org_slug": "phase5-org"},
    )
    assert login.status_code == 200
    token = login.json()["session_id"]
    created = client.post(
        "/api/v1/projects",
        json={"name": "Phase 5 Project"},
        headers={"X-Saturn-Session-Id": token, "Idempotency-Key": "phase5-project"},
    )
    assert created.status_code == 201
    return token, created.json()["id"]


def _upload_document(client: TestClient, headers: dict, project_id: str) -> tuple[str, str]:
    created = client.post(
        "/api/v1/documents",
        json={"project_id": project_id, "title": "Runbook"},
        headers=headers,
    )
    assert created.status_code == 201
    document_id = created.json()["id"]
    uploaded = client.post(
        f"/api/v1/documents/{document_id}/sources",
        json={
            "filename": "runbook.md",
            "media_type": "text/markdown",
            "content_base64": base64.b64encode(
                b"# Operations\n\nBilling retry steps live here.\n\n## Archive\n\nOld notes"
            ).decode(),
        },
        headers=headers,
    )
    assert uploaded.status_code == 201
    return document_id, uploaded.json()["parse_job"]["id"]


def _context_for_token(session, token: str):
    from saturn.access.context import AuthContext
    from saturn.identity.service import IdentityService

    user_session = IdentityService(session).get_session(token)
    return AuthContext(
        user_id=user_session.user_id,
        org_id=user_session.org_id,
        session_id=token,
    )
