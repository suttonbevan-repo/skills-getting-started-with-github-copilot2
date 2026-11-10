import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    original_activities = copy.deepcopy(activities)
    with TestClient(app) as test_client:
        yield test_client
    activities.clear()
    activities.update(original_activities)


def test_get_activities_returns_available_activities(client):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert "Chess Club" in response.json()


def test_signup_adds_participant(client):
    # Arrange
    email = "new-student@mergington.edu"

    # Act
    response = client.post("/activities/Art%20Studio/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in client.get("/activities").json()["Art Studio"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = "new-student@mergington.edu"
    client.post("/activities/Art%20Studio/signup", params={"email": email})

    # Act
    response = client.post("/activities/Art%20Studio/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"


def test_signup_rejects_unknown_activity(client):
    # Arrange
    email = "new-student@mergington.edu"

    # Act
    response = client.post("/activities/Unknown%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client):
    # Arrange
    email = "new-student@mergington.edu"
    client.post("/activities/Art%20Studio/signup", params={"email": email})

    # Act
    response = client.delete("/activities/Art%20Studio/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email not in client.get("/activities").json()["Art Studio"]["participants"]


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    email = "new-student@mergington.edu"

    # Act
    response = client.delete("/activities/Unknown%20Club/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_rejects_unregistered_participant(client):
    # Arrange
    email = "new-student@mergington.edu"

    # Act
    response = client.delete("/activities/Art%20Studio/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"