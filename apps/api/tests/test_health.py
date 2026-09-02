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


def test_security_headers_are_emitted() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["permissions-policy"] == "camera=(), microphone=(), geolocation=()"
    assert response.headers["cross-origin-resource-policy"] == "cross-origin"
    assert response.headers["x-permitted-cross-domain-policies"] == "none"
    assert response.headers["content-security-policy"] == "default-src 'none'; frame-ancestors 'none'"
    assert response.headers["x-request-id"]


def test_request_id_is_preserved_when_supplied() -> None:
    response = client.get("/health", headers={"x-request-id": "step40-test-request"})
    assert response.status_code == 200
    assert response.headers["x-request-id"] == "step40-test-request"


def test_hsts_is_emitted_for_public_https_proxy() -> None:
    response = client.get("/health", headers={"x-forwarded-proto": "https"})
    assert response.status_code == 200
    assert response.headers["strict-transport-security"] == "max-age=31536000; includeSubDomains"


def test_production_web_origin_has_cors_preflight_support() -> None:
    response = client.options(
        "/auth/login",
        headers={
            "Origin": "https://buildcost-pro-production.up.railway.app",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "https://buildcost-pro-production.up.railway.app"
    assert "POST" in response.headers["access-control-allow-methods"]
    assert "content-type" in response.headers["access-control-allow-headers"].lower()
