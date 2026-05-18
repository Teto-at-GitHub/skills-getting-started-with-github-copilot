from copy import deepcopy
from urllib.parse import quote

import pytest
from httpx import TestClient

from src.app import app, activities


ORIGINAL_ACTIVITIES = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    # Reset the in-memory activities dict before each test
    activities.clear()
    activities.update(deepcopy(ORIGINAL_ACTIVITIES))


@pytest.fixture
def client():
    return TestClient(app)


def _activity_path(name: str, tail: str) -> str:
    return f"/activities/{quote(name)}/{tail}"


def test_get_activities(client):
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_success(client):
    email = "newstudent@test.edu"
    r = client.post(_activity_path("Chess Club", "signup"), params={"email": email})
    assert r.status_code == 200
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate(client):
    email = "michael@mergington.edu"
    r = client.post(_activity_path("Chess Club", "signup"), params={"email": email})
    assert r.status_code == 400


def test_remove_participant(client):
    email = "michael@mergington.edu"
    r = client.delete(_activity_path("Chess Club", "participants"), params={"email": email})
    assert r.status_code == 200
    assert email not in activities["Chess Club"]["participants"]
