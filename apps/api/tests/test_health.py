from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "buildcost-pro-api",
        "version": "1.0.0",
    }


def test_hsts_is_emitted_for_public_https_proxy() -> None:
    response = client.get("/health", headers={"x-forwarded-proto": "https"})
    assert response.status_code == 200
    assert response.headers["strict-transport-security"] == "max-age=31536000; includeSubDomains"
