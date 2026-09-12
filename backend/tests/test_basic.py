import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register():
    """Test user registration"""
    response = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "SecurePassword123"
    })
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

def test_register_duplicate():
    """Test duplicate registration"""
    # Register first user
    client.post("/api/v1/auth/register", json={
        "email": "test2@example.com",
        "username": "testuser2",
        "password": "SecurePassword123"
    })
    
    # Try to register again
    response = client.post("/api/v1/auth/register", json={
        "email": "test2@example.com",
        "username": "testuser2",
        "password": "SecurePassword123"
    })
    assert response.status_code == 400

def test_login():
    """Test user login"""
    # First register
    client.post("/api/v1/auth/register", json={
        "email": "login@example.com",
        "username": "loginuser",
        "password": "SecurePassword123"
    })
    
    # Then login
    response = client.post("/api/v1/auth/login", json={
        "email": "login@example.com",
        "password": "SecurePassword123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_invalid():
    """Test login with wrong password"""
    response = client.post("/api/v1/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "WrongPassword123"
    })
    assert response.status_code == 401