"""
Integration tests for the Reports feature.
Tests the /reports/usage endpoint with database interactions.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.user import User
from app.models.calculation import Calculation

client = TestClient(app)


def test_usage_report_no_calculations(db_session: Session, test_user: User):
    """Test usage report when user has no calculations."""
    access_token = User.create_access_token({"sub": str(test_user.id)})
    
    response = client.get(
        "/reports/usage",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_calculations"] == 0
    assert data["by_type"] == {}
    assert data["average_result"] is None


def test_usage_report_with_calculations(db_session: Session, test_user: User):
    """Test usage report with multiple calculations."""
    access_token = User.create_access_token({"sub": str(test_user.id)})
    
    # Create test calculations
    calcs = [
        Calculation(user_id=test_user.id, type="addition", inputs={"a": 5, "b": 3}, result=8),
        Calculation(user_id=test_user.id, type="addition", inputs={"a": 10, "b": 2}, result=12),
        Calculation(user_id=test_user.id, type="subtraction", inputs={"a": 20, "b": 5}, result=15),
        Calculation(user_id=test_user.id, type="multiplication", inputs={"a": 3, "b": 4}, result=12),
    ]
    for calc in calcs:
        db_session.add(calc)
    db_session.commit()
    
    response = client.get(
        "/reports/usage",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_calculations"] == 4
    assert data["by_type"]["addition"] == 2
    assert data["by_type"]["subtraction"] == 1
    assert data["by_type"]["multiplication"] == 1
    # Average: (8 + 12 + 15 + 12) / 4 = 11.75
    assert data["average_result"] == 11.75


def test_usage_report_unauthorized(db_session: Session):
    """Test usage report without authentication."""
    response = client.get("/reports/usage")
    assert response.status_code == 401


def test_usage_report_only_shows_user_calculations(db_session: Session, test_user: User):
    """Test that usage report only includes current user's calculations."""
    # Create another user
    other_user = User(
        username="otheruser",
        email="other@example.com",
        hashed_password="fakehash",
        first_name="Other",
        last_name="User"
    )
    db_session.add(other_user)
    db_session.commit()
    db_session.refresh(other_user)
    
    # Add calculations for both users
    db_session.add(Calculation(
        user_id=test_user.id, 
        type="addition", 
        inputs={"a": 1, "b": 1}, 
        result=2
    ))
    db_session.add(Calculation(
        user_id=other_user.id, 
        type="addition", 
        inputs={"a": 5, "b": 5}, 
        result=10
    ))
    db_session.commit()
    
    access_token = User.create_access_token({"sub": str(test_user.id)})
    
    response = client.get(
        "/reports/usage",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    # Should only see test_user's calculation
    assert data["total_calculations"] == 1
    assert data["average_result"] == 2.0
