"""
Tests for the Mergington High School Activities API

Tests are organized using the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test fixtures and initial state
- Act: Execute the action being tested
- Assert: Verify the results
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add src directory to Python path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Fixture to provide a TestClient instance for all tests"""
    return TestClient(app)


class TestRootEndpoint:
    """Tests for the GET / endpoint"""

    def test_root_redirect(self, client):
        """
        Test that GET / redirects to /static/index.html
        
        Arrange: Create a TestClient instance
        Act: Make a GET request to /
        Assert: Verify redirect response with status 307 and correct Location header
        """
        # Arrange
        expected_redirect_url = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_redirect_url


class TestActivitiesEndpoint:
    """Tests for the GET /activities endpoint"""

    def test_get_all_activities(self, client):
        """
        Test that GET /activities returns all available activities
        
        Arrange: Create a TestClient instance
        Act: Make a GET request to /activities
        Assert: Verify 200 status, response is dict with expected activities and structure
        """
        # Arrange
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Soccer Club",
            "Art Club",
            "Music Band",
            "Debate Club",
            "Science Club"
        ]

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert response.status_code == 200
        assert isinstance(activities, dict)
        assert set(activities.keys()) == set(expected_activities)
        
        # Verify structure of each activity
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_for_activity(self, client):
        """
        Test that a student can successfully sign up for an activity
        
        Arrange: Create a TestClient instance and define a test email
        Act: Make a POST request to sign up for Chess Club
        Assert: Verify 200 status and student email appears in participants list
        """
        # Arrange
        activity_name = "Chess Club"
        student_email = "alice@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )

        # Assert
        assert response.status_code == 200
        assert "message" in response.json()
        
        # Verify student was added to activity
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert student_email in activities[activity_name]["participants"]

    def test_signup_for_different_activity(self, client):
        """
        Test that a student can sign up for an activity with no participants
        
        Arrange: Create a TestClient and define test email for an empty activity
        Act: Make a POST request to sign up for Basketball Team
        Assert: Verify 200 status and email is in participants list
        """
        # Arrange
        activity_name = "Basketball Team"
        student_email = "bob@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )

        # Assert
        assert response.status_code == 200
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert student_email in activities[activity_name]["participants"]


class TestUnregisterEndpoint:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_from_activity(self, client):
        """
        Test that a student can successfully unregister from an activity
        
        Arrange: Sign up a student for an activity, then prepare to unregister
        Act: Make a DELETE request to unregister the student
        Assert: Verify 200 status and student email is removed from participants list
        """
        # Arrange
        activity_name = "Chess Club"
        student_email = "charlie@mergington.edu"
        
        # First, sign up the student
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": student_email}
        )

        # Assert
        assert response.status_code == 200
        assert "message" in response.json()
        
        # Verify student was removed from activity
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert student_email not in activities[activity_name]["participants"]

    def test_unregister_from_different_activity(self, client):
        """
        Test that a student can unregister from an activity with pre-existing participants
        
        Arrange: Create TestClient and use an activity that has existing participants
        Act: Make a DELETE request to unregister an existing participant
        Assert: Verify 200 status and email is removed from participants list
        """
        # Arrange
        activity_name = "Chess Club"
        # Chess Club has pre-populated participants from the app initialization
        student_email = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": student_email}
        )

        # Assert
        assert response.status_code == 200
        
        # Verify student was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert student_email not in activities[activity_name]["participants"]
