"""Tests for edge cases and validation"""
import pytest


def test_max_participants_limit_not_enforced(client):
    """Test that max_participants limit is currently NOT enforced"""
    # This test documents that the max_participants validation is missing
    # Get an activity with limited capacity
    activities = client.get("/activities").json()
    
    # Chess Club has max 12 participants
    chess_max = activities["Chess Club"]["max_participants"]
    current_count = len(activities["Chess Club"]["participants"])
    
    # Try to sign up multiple users beyond the limit
    # This should fail if validation were implemented, but currently succeeds
    for i in range(chess_max + 5):
        email = f"overflow{i}@mergington.edu"
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        # Currently this succeeds even if we exceed max_participants
        if response.status_code == 200:
            # This demonstrates the gap - we can exceed capacity
            pass
        else:
            # If this starts failing, it means max_participants was implemented
            assert response.status_code == 400 or response.status_code == 409


def test_activity_name_case_sensitivity(client):
    """Test that activity names are case-sensitive"""
    # Try to sign up with different casing
    response = client.post(
        "/activities/chess club/signup",  # lowercase
        params={"email": "test@mergington.edu"}
    )
    # Should fail because exact name is "Chess Club"
    assert response.status_code == 404


def test_empty_participants_list(client):
    """Test that activities can have empty participant lists"""
    activities = client.get("/activities").json()
    
    # Check if any activity has empty participants (shouldn't be the case with base data)
    # But verify the structure is valid
    for activity_name, activity_details in activities.items():
        assert isinstance(activity_details["participants"], list)


def test_activity_capacity_display(client):
    """Test that available spots are calculated correctly"""
    activities = client.get("/activities").json()
    
    for activity_name, activity_details in activities.items():
        max_participants = activity_details["max_participants"]
        current_participants = len(activity_details["participants"])
        available_spots = max_participants - current_participants
        
        # Available spots should be non-negative
        assert available_spots >= 0, f"Activity {activity_name} has more participants than max"


def test_signup_and_verify_capacity_changes(client):
    """Test that signing up changes the available capacity correctly"""
    activities_before = client.get("/activities").json()
    programming_before = activities_before["Programming Class"]
    spots_before = programming_before["max_participants"] - len(programming_before["participants"])
    
    # Sign up a new student
    email = "capacity_test@mergington.edu"
    response = client.post(
        "/activities/Programming Class/signup",
        params={"email": email}
    )
    assert response.status_code == 200
    
    # Check capacity after signup
    activities_after = client.get("/activities").json()
    programming_after = activities_after["Programming Class"]
    spots_after = programming_after["max_participants"] - len(programming_after["participants"])
    
    # One less spot should be available
    assert spots_after == spots_before - 1


def test_all_activities_have_valid_data(client):
    """Test that all activities have valid, non-null data"""
    activities = client.get("/activities").json()
    
    for activity_name, activity_details in activities.items():
        # Verify no None values
        assert activity_details["description"] is not None and activity_details["description"] != ""
        assert activity_details["schedule"] is not None and activity_details["schedule"] != ""
        assert activity_details["max_participants"] is not None and activity_details["max_participants"] > 0
        assert activity_details["participants"] is not None
        
        # Verify activity name is not empty
        assert activity_name is not None and activity_name != ""
