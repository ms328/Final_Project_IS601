"""
E2E tests for the Reports feature.
Tests the full workflow of viewing usage statistics in the UI.
"""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app

client = TestClient(app)


def register_and_login(username_suffix=""):
    """Helper to register and login a user with unique username."""
    username = f"reportuser{username_suffix}"
    user_data = {
        "username": username,
        "email": f"{username}@test.com",
        "password": "Test123!",
        "confirm_password": "Test123!",
        "first_name": "Report",
        "last_name": "User"
    }
    
    # Register
    reg_resp = client.post("/auth/register", json=user_data)
    assert reg_resp.status_code == 201, f"Registration failed: {reg_resp.text}"
    
    # Login
    login_resp = client.post(
        "/auth/login",
        json={"username": username, "password": "Test123!"},
    )
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    return login_resp.json()["access_token"]


def test_reports_endpoint_returns_usage_stats():
    """Test that reports endpoint returns correct usage statistics."""
    token = register_and_login(str(uuid4())[:8])
    headers = {"Authorization": f"Bearer {token}"}
    
    # Initially no calculations
    response = client.get("/reports/usage", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_calculations"] == 0
    
    # Create some calculations
    client.post(
        "/calculations",
        json={"type": "addition", "inputs": [5, 3]},
        headers=headers,
    )
    client.post(
        "/calculations",
        json={"type": "subtraction", "inputs": [10, 2]},
        headers=headers,
    )
    client.post(
        "/calculations",
        json={"type": "addition", "inputs": [7, 3]},
        headers=headers,
    )
    
    # Check updated stats
    response = client.get("/reports/usage", headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_calculations"] == 3
    assert data["by_type"]["addition"] == 2
    assert data["by_type"]["subtraction"] == 1
    assert data["average_result"] is not None


def test_reports_requires_authentication():
    """Test that reports endpoint requires authentication."""
    response = client.get("/reports/usage")
    assert response.status_code == 401
    assert "detail" in response.json()


def test_reports_average_calculation():
    """Test that average result is calculated correctly."""
    token = register_and_login(str(uuid4())[:8])
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create calculations with known results
    client.post(
        "/calculations",
        json={"type": "addition", "inputs": [10, 0]},  # result: 10
        headers=headers,
    )
    client.post(
        "/calculations",
        json={"type": "addition", "inputs": [20, 0]},  # result: 20
        headers=headers,
    )
    
    response = client.get("/reports/usage", headers=headers)
    data = response.json()
    
    # Average should be (10 + 20) / 2 = 15
    assert data["average_result"] == 15.0
