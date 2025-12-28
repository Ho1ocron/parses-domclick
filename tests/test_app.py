import parser_domclick.app as app_mod
from fastapi.testclient import TestClient

# Prevent the lifespan from waiting for a real Selenium server in CI/test runs
app_mod.is_selenium_ready = lambda host, port: True

client = TestClient(app_mod.app)


def test_root_endpoint():
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("name") == "Cian Parser API"


def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json().get("status") == "healthy"
