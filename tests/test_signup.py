"""Tests for POST /activities/{activity_name}/signup endpoint"""
import pytest


def test_signup_success(client):
    """Test successfully signing up a student for an activity"""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "test@mergington.edu"}
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "test@mergington.edu" in data["message"]
    assert "Chess Club" in data["message"]


def test_signup_adds_participant(client):
    """Test that signup actually adds the participant to the activity"""
    email = "newstudent@mergington.edu"
    
    # First, get the initial participants
    activities_before = client.get("/activities").json()
    initial_count = len(activities_before["Chess Club"]["participants"])
    
    # Sign up
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email}
    )
    assert response.status_code == 200
    
    # Verify participant was added
    activities_after = client.get("/activities").json()
    final_count = len(activities_after["Chess Club"]["participants"])
    
    assert final_count == initial_count + 1
    assert email in activities_after["Chess Club"]["participants"]


def test_signup_nonexistent_activity(client):
    """Test signing up for an activity that doesn't exist"""
    response = client.post(
        "/activities/Nonexistent Club/signup",
        params={"email": "test@mergington.edu"}
    )
    assert response.status_code == 404
    
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_signup_duplicate_email(client):
    """Test that signing up with a duplicate email returns 400"""
    # Use an email that already exists in an activity
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"}  # Already in Chess Club
    )
    assert response.status_code == 400
    
    data = response.json()
    assert "detail" in data
    assert "already" in data["detail"].lower()


def test_signup_same_email_different_activities(client):
    """Test that the same email can sign up for different activities"""
    email = "multisport@mergington.edu"
    
    # Sign up for first activity
    response1 = client.post(
        "/activities/Chess Club/signup",
        params={"email": email}
    )
    assert response1.status_code == 200
    
    # Sign up for second activity - should succeed
    response2 = client.post(
        "/activities/Programming Class/signup",
        params={"email": email}
    )
    assert response2.status_code == 200
    
    # Verify both signups worked
    activities = client.get("/activities").json()
    assert email in activities["Chess Club"]["participants"]
    assert email in activities["Programming Class"]["participants"]


def test_signup_email_format_validation(client):
    """Test signup with various email formats"""
    # Valid email formats should all work (no validation is enforced in the app)
    valid_emails = [
        "simple@mergington.edu",
        "firstname.lastname@mergington.edu",
        "user+tag@mergington.edu"
    ]
    
    for idx, email in enumerate(valid_emails):
        # Use different activities to avoid duplicate email errors
        activities = client.get("/activities").json()
        activity_name = list(activities.keys())[idx]
        
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        # Current implementation doesn't validate, so should succeed
        assert response.status_code == 200
