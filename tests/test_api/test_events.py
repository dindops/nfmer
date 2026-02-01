import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from nfmer.api.v1.api import api
from nfmer.db_handler import DatabaseHandler, get_db
from nfmer.models import Event

client = TestClient(api)

mock_events = [
    Event(
        id="20240315-1900-concert-hall",
        location="Concert Hall",
        date="2024-03-15",
        hour="19:00",
        url="https://example.com/event/1",
    ),
    Event(
        id="20240420-2000-opera-house",
        location="Opera House",
        date="2024-04-20",
        hour="20:00",
        url="https://example.com/event/2",
    ),
]


@pytest.fixture
def mock_db(mocker: MockerFixture) -> DatabaseHandler:
    db = mocker.MagicMock(spec=DatabaseHandler)
    db.get_all_events.return_value = [event.id for event in mock_events]
    db.get_event_by_id.side_effect = lambda id: (
        mock_events[0] if id == "20240315-1900-concert-hall"
        else mock_events[1] if id == "20240420-2000-opera-house"
        else None
    )
    return db


@pytest.fixture(autouse=True)
def override_dependency(mock_db: DatabaseHandler) -> None:
    api.dependency_overrides[get_db] = lambda: mock_db
    yield
    api.dependency_overrides = {}


def test_get_all_events() -> None:
    response = client.get("/events/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0] == "20240315-1900-concert-hall"
    assert data[1] == "20240420-2000-opera-house"


def test_get_event_by_id() -> None:
    response = client.get("/events/20240315-1900-concert-hall")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "20240315-1900-concert-hall"
    assert data["location"] == "Concert Hall"
    assert data["date"] == "2024-03-15"
    assert data["hour"] == "19:00"
    assert data["url"] == "https://example.com/event/1"


def test_get_event_not_found() -> None:
    response = client.get("/events/non-existent-event")
    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"
