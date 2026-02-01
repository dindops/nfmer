import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from nfmer.api.v1.api import api
from nfmer.db_handler import DatabaseHandler, get_db
from nfmer.models import Composer, Composition, Event

client = TestClient(api)

mock_composers = [
    Composer(id=1, composer_name="Johann Sebastian Bach", compositions=[]),
    Composer(id=2, composer_name="Wolfgang Amadeus Mozart", compositions=[]),
]

mock_events = [
    Event(id="event-1", location="Concert Hall", date="2024-03-15", hour="19:00", url="https://example.com/1"),
    Event(id="event-2", location="Opera House", date="2024-04-20", hour="20:00", url="https://example.com/2"),
]

mock_compositions = [
    Composition(id=1, composition_name="Brandenburg Concerto No. 3", composer_id=1, composer=mock_composers[0]),
    Composition(id=2, composition_name="Symphony No. 40", composer_id=2, composer=mock_composers[1]),
]

mock_composition_full = Composition(
    id=1,
    composition_name="Brandenburg Concerto No. 3",
    composer_id=1,
    composer=mock_composers[0],
    events=[mock_events[0]],
)


@pytest.fixture
def mock_db(mocker: MockerFixture) -> DatabaseHandler:
    db = mocker.MagicMock(spec=DatabaseHandler)
    db.get_all_compositions.return_value = mock_compositions
    db.search_compositions_by_name.return_value = [mock_compositions[0]]
    db.get_composition_by_id.side_effect = lambda id: (
        mock_composition_full if id == 1 else mock_compositions[1] if id == 2 else None
    )
    return db


@pytest.fixture(autouse=True)
def override_dependency(mock_db: DatabaseHandler) -> None:
    api.dependency_overrides[get_db] = lambda: mock_db
    yield
    api.dependency_overrides = {}


def test_get_all_compositions() -> None:
    response = client.get("/compositions/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["composition_name"] == "Brandenburg Concerto No. 3"
    assert data[1]["composition_name"] == "Symphony No. 40"


def test_search_compositions() -> None:
    response = client.get("/compositions/?search=Brandenburg")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["composition_name"] == "Brandenburg Concerto No. 3"


def test_get_composition_by_id() -> None:
    response = client.get("/compositions/1")
    assert response.status_code == 200
    data = response.json()
    assert data["composition_name"] == "Brandenburg Concerto No. 3"
    assert "composer" in data
    assert data["composer"]["composer_name"] == "Johann Sebastian Bach"
    assert "events" in data
    assert len(data["events"]) == 1
    assert data["events"][0]["location"] == "Concert Hall"


def test_get_composition_not_found() -> None:
    response = client.get("/compositions/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Composition not found"
