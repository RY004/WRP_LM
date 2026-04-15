from fastapi.testclient import TestClient

from saturn.api.app import create_app
from saturn.bootstrap.container import ApplicationContainer
from saturn.bootstrap.settings import Settings


def test_app_boots_with_container_and_healthcheck(tmp_path) -> None:
    settings = Settings(app_env="test", storage_filesystem_root=tmp_path)
    app = create_app(settings)
    client = TestClient(app)

    response = client.get("/healthz", headers={"X-Request-ID": "req-test"})

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "Saturn", "environment": "test"}
    assert response.headers["X-Request-ID"] == "req-test"
    assert isinstance(app.state.container, ApplicationContainer)


def test_idempotency_header_is_reflected(tmp_path) -> None:
    app = create_app(Settings(app_env="test", storage_filesystem_root=tmp_path))
    client = TestClient(app)

    response = client.get("/readyz", headers={"Idempotency-Key": "idem-1"})

    assert response.status_code == 200
    assert response.headers["Idempotency-Key"] == "idem-1"
