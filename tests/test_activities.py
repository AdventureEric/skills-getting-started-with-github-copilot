"""Tests for GET /activities endpoint"""
import pytest


def test_get_activities_success(client):
    """Test successfully retrieving all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    data = response.json()
    # Should return a dictionary of activities
    assert isinstance(data, dict)
    assert len(data) > 0


def test_get_activities_structure(client):
    """Test that activities have the correct structure"""
    response = client.get("/activities")
    data = response.json()
    
    # Check that each activity has required fields
    for activity_name, activity_details in data.items():
        assert isinstance(activity_name, str)
        assert "description" in activity_details
        assert "schedule" in activity_details
        assert "max_participants" in activity_details
        assert "participants" in activity_details
        
        # Verify field types
        assert isinstance(activity_details["description"], str)
        assert isinstance(activity_details["schedule"], str)
        assert isinstance(activity_details["max_participants"], int)
        assert isinstance(activity_details["participants"], list)


def test_get_activities_participants_are_emails(client):
    """Test that participants in activities are email addresses"""
    response = client.get("/activities")
    data = response.json()
    
    for activity_name, activity_details in data.items():
        for participant in activity_details["participants"]:
            assert isinstance(participant, str)
            assert "@" in participant, f"Participant {participant} should be an email"


def test_get_activities_contains_expected_activities(client):
    """Test that the response contains expected activities"""
    response = client.get("/activities")
    data = response.json()
    
    expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
    for activity in expected_activities:
        assert activity in data, f"Expected activity '{activity}' not found"
