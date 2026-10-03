from fastapi.testclient import TestClient

import app.modules.health.api as health_api
from app.main import app

client = TestClient(app, base_url="http://localhost")


def test_liveness() -> None:
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers.get("X-Request-ID")


def test_meta_endpoint() -> None:
    response = client.get("/api/v1/meta")
    assert response.status_code == 200
    assert response.json()["api_version"] == "v1"


def test_readiness_when_database_available(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    async def ready() -> bool:
        return True

    monkeypatch.setattr(health_api, "ping_database", ready)
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_readiness_when_database_unavailable(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    async def not_ready() -> bool:
        return False

    monkeypatch.setattr(health_api, "ping_database", not_ready)
    response = client.get("/health/ready")
    assert response.status_code == 503
