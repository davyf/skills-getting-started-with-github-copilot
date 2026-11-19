from src.app import activities


def test_root_redirects_to_static_index(client):
    # Arrange
    url = "/"

    # Act
    response = client.get(url, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities(client):
    # Arrange
    expected_keys = {"description", "schedule", "max_participants", "participants"}

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert len(data) == len(activities)
    for details in data.values():
        assert set(details) == expected_keys


def test_signup_adds_participant(client):
    # Arrange
    activity = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity}"}
    assert email in activities[activity]["participants"]


def test_signup_rejects_duplicate(client):
    # Arrange
    activity = "Chess Club"
    email = activities[activity]["participants"][0]
    count_before = len(activities[activity]["participants"])

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]
    assert len(activities[activity]["participants"]) == count_before


def test_signup_unknown_activity_returns_404(client):
    # Arrange
    email = "newstudent@mergington.edu"

    # Act
    response = client.post("/activities/Underwater Basket Weaving/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client):
    # Arrange
    activity = "Chess Club"
    email = activities[activity]["participants"][0]

    # Act
    response = client.delete(f"/activities/{activity}/unregister", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity}"}
    assert email not in activities[activity]["participants"]


def test_unregister_not_signed_up_returns_404(client):
    # Arrange
    activity = "Chess Club"
    email = "notregistered@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/unregister", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_unknown_activity_returns_404(client):
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.delete("/activities/Underwater Basket Weaving/unregister", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_then_unregister_round_trip(client):
    # Arrange
    activity = "Basketball Team"
    email = "roundtrip@mergington.edu"
    original = list(activities[activity]["participants"])

    # Act
    signup = client.post(f"/activities/{activity}/signup", params={"email": email})
    unregister = client.delete(f"/activities/{activity}/unregister", params={"email": email})

    # Assert
    assert signup.status_code == 200
    assert unregister.status_code == 200
    assert client.get("/activities").json()[activity]["participants"] == original
