"""Tests for DELETE /activities/{activity_name}/signup endpoint"""
import pytest


def test_unregister_success(client):
    """Test successfully unregistering a participant from an activity"""
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"}  # Exists in Chess Club
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "michael@mergington.edu" in data["message"]


def test_unregister_removes_participant(client):
    """Test that unregister actually removes the participant from the activity"""
    email = "michael@mergington.edu"
    
    # Verify participant exists
    activities_before = client.get("/activities").json()
    assert email in activities_before["Chess Club"]["participants"]
    initial_count = len(activities_before["Chess Club"]["participants"])
    
    # Unregister
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": email}
    )
    assert response.status_code == 200
    
    # Verify participant was removed
    activities_after = client.get("/activities").json()
    final_count = len(activities_after["Chess Club"]["participants"])
    
    assert final_count == initial_count - 1
    assert email not in activities_after["Chess Club"]["participants"]


def test_unregister_nonexistent_activity(client):
    """Test unregistering from an activity that doesn't exist"""
    response = client.delete(
        "/activities/Nonexistent Club/signup",
        params={"email": "test@mergington.edu"}
    )
    assert response.status_code == 404
    
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_unregister_participant_not_found(client):
    """Test unregistering a participant that is not in the activity"""
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "notaparticipant@mergington.edu"}
    )
    assert response.status_code == 404
    
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_unregister_twice(client):
    """Test that unregistering twice for the same participant fails on second attempt"""
    email = "testuser@mergington.edu"
    
    # First signup
    signup_response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email}
    )
    assert signup_response.status_code == 200
    
    # First unregister - should succeed
    unregister1 = client.delete(
        "/activities/Chess Club/signup",
        params={"email": email}
    )
    assert unregister1.status_code == 200
    
    # Second unregister - should fail with 404
    unregister2 = client.delete(
        "/activities/Chess Club/signup",
        params={"email": email}
    )
    assert unregister2.status_code == 404


def test_unregister_preserves_other_participants(client):
    """Test that unregistering one participant doesn't affect others"""
    # Get initial state
    activities_before = client.get("/activities").json()
    chess_participants = activities_before["Chess Club"]["participants"].copy()
    
    if len(chess_participants) > 1:
        # Remove first participant
        participant_to_remove = chess_participants[0]
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": participant_to_remove}
        )
        assert response.status_code == 200
        
        # Verify other participants are still there
        activities_after = client.get("/activities").json()
        remaining_participants = activities_after["Chess Club"]["participants"]
        
        for participant in chess_participants[1:]:
            assert participant in remaining_participants
