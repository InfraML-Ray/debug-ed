from fastapi.testclient import TestClient

from app.main import create_app


def test_api_boots_and_serves_health():
    with TestClient(create_app()) as client:
        response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
