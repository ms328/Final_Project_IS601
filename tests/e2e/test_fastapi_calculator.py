from datetime import datetime, timezone
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.calculation import Calculation

client = TestClient(app)

# =============================================================================
# Fixtures & Helpers
# =============================================================================


def _parse_datetime(dt_str: str) -> datetime:
    """Parse ISO datetime string into timezone-aware datetime."""
    if dt_str.endswith("Z"):
        dt_str = dt_str.replace("Z", "+00:00")
    return datetime.fromisoformat(dt_str)


def register_and_login(user_data: dict) -> dict:
    """
    Registers a new user and logs in.
    Returns the login token payload.
    """
    reg_resp = client.post("/auth/register", json=user_data)
    assert reg_resp.status_code == 201, f"Registration failed: {reg_resp.text}"

    login_payload = {
        "username": user_data["username"],
        "password": user_data["password"]
    }
    login_resp = client.post("/auth/login", json=login_payload)
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"

    return login_resp.json()


# =============================================================================
# Health & Authentication Tests
# =============================================================================

def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_user_registration_and_login():
    user = {
        "first_name": "Alice",
        "last_name": "Tester",
        "email": f"alice{uuid4()}@example.com",
        "username": f"alice_{uuid4()}",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!"
    }

    token_data = register_and_login(user)

    required_fields = [
        "access_token",
        "refresh_token",
        "token_type",
        "expires_at",
        "user_id",
        "username",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_verified"
    ]

    for field in required_fields:
        assert field in token_data

    assert token_data["token_type"].lower() == "bearer"
    assert token_data["is_active"] is True

    expires_at = _parse_datetime(token_data["expires_at"])
    assert expires_at > datetime.now(timezone.utc)


# =============================================================================
# Calculation CRUD Integration Tests
# =============================================================================

def test_create_calculation_addition():
    user = {
        "first_name": "Calc",
        "last_name": "Adder",
        "email": f"add{uuid4()}@example.com",
        "username": f"adder_{uuid4()}",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!"
    }
    token = register_and_login(user)["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "type": "addition",
        "inputs": [10, 5, 2]
    }

    resp = client.post("/calculations", json=payload, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["result"] == 17


def test_create_calculation_subtraction():
    user = {
        "first_name": "Calc",
        "last_name": "Sub",
        "email": f"sub{uuid4()}@example.com",
        "username": f"sub_{uuid4()}",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!"
    }
    token = register_and_login(user)["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "type": "subtraction",
        "inputs": [10, 3, 2]
    }

    resp = client.post("/calculations", json=payload, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["result"] == 5


def test_create_calculation_multiplication():
    user = {
        "first_name": "Calc",
        "last_name": "Mult",
        "email": f"mult{uuid4()}@example.com",
        "username": f"mult_{uuid4()}",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!"
    }
    token = register_and_login(user)["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "type": "multiplication",
        "inputs": [2, 3, 4]
    }

    resp = client.post("/calculations", json=payload, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["result"] == 24


def test_create_calculation_division():
    user = {
        "first_name": "Calc",
        "last_name": "Div",
        "email": f"div{uuid4()}@example.com",
        "username": f"div_{uuid4()}",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!"
    }
    token = register_and_login(user)["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "type": "division",
        "inputs": [100, 2, 5]
    }

    resp = client.post("/calculations", json=payload, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["result"] == 10


def test_list_get_update_delete_calculation():
    user = {
        "first_name": "Calc",
        "last_name": "CRUD",
        "email": f"crud{uuid4()}@example.com",
        "username": f"crud_{uuid4()}",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!"
    }
    token = register_and_login(user)["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create
    create_resp = client.post(
        "/calculations",
        json={"type": "multiplication", "inputs": [3, 4]},
        headers=headers
    )
    assert create_resp.status_code == 201
    calc_id = create_resp.json()["id"]

    # List
    list_resp = client.get("/calculations", headers=headers)
    assert any(c["id"] == calc_id for c in list_resp.json())

    # Get
    get_resp = client.get(f"/calculations/{calc_id}", headers=headers)
    assert get_resp.status_code == 200

    # Update
    update_resp = client.put(
        f"/calculations/{calc_id}",
        json={"inputs": [5, 6]},
        headers=headers
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["result"] == 30

    # Delete
    delete_resp = client.delete(
        f"/calculations/{calc_id}",
        headers=headers
    )
    assert delete_resp.status_code == 204

    # Confirm deletion
    confirm_resp = client.get(f"/calculations/{calc_id}", headers=headers)
    assert confirm_resp.status_code == 404


# =============================================================================
# Unit Tests (Model-Level)
# =============================================================================

def test_model_addition():
    calc = Calculation.create("addition", uuid4(), [1, 2, 3])
    assert calc.get_result() == 6


def test_model_subtraction():
    calc = Calculation.create("subtraction", uuid4(), [10, 3, 2])
    assert calc.get_result() == 5


def test_model_multiplication():
    calc = Calculation.create("multiplication", uuid4(), [2, 3, 4])
    assert calc.get_result() == 24


def test_model_division():
    calc = Calculation.create("division", uuid4(), [100, 2, 5])
    assert calc.get_result() == 10

    with pytest.raises(ValueError):
        Calculation.create("division", uuid4(), [10, 0]).get_result()
