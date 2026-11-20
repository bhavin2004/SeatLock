from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_unknown_api_endpoint():
    response = client.get("/api/v1/unknown")
    assert response.status_code == 404
    assert response.json() == {"detail":"Not Found"}