import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_api_status():
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    assert "version" in response.json()

def test_hello():
    response = client.get("/api/v1/hello")
    assert response.status_code == 200
    assert "message" in response.json()

def test_test_request():
    response = client.post("/api/v1/test-request", json={"test": "data"})
    assert response.status_code == 200
    assert response.json()["status"] == "processed"