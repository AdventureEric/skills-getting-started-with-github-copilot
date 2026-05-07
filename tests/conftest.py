import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy


# Store the original activities for resetting between tests
ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    # Reset activities to original state before each test
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))
    
    yield TestClient(app)
    
    # Cleanup after test
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))
