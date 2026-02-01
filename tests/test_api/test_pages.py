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
]

mock_compositions = [
    Composition(id=1, composition_name="Brandenburg Concerto No. 3", composer_id=1, composer=mock_composers[0]),
    Composition(id=2, composition_name="Symphony No. 40", composer_id=2, composer=mock_composers[1]),
]

mock_composer_full = Composer(
    id=1,
    composer_name="Johann Sebastian Bach",
    compositions=[mock_compositions[0]],
)

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
    db.search_composers_by_name.return_value = [mock_composers[0]]
    db.search_compositions_by_name.return_value = [mock_compositions[0]]
    db.get_composer_by_id.side_effect = lambda id: (
        mock_composer_full if id == 1 else None
    )
    db.get_composition_by_id.side_effect = lambda id: (
        mock_composition_full if id == 1 else None
    )
    return db


@pytest.fixture(autouse=True)
def override_dependency(mock_db: DatabaseHandler) -> None:
    api.dependency_overrides[get_db] = lambda: mock_db
    yield
    api.dependency_overrides = {}


def test_index_page() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "NFMinder Search" in response.text


def test_search_results_composers_empty() -> None:
    response = client.get("/search/?q=&type=composers")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Enter your search terms above" in response.text


def test_search_results_composers_with_query() -> None:
    response = client.get("/search/?q=Bach&type=composers")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Johann Sebastian Bach" in response.text


def test_search_results_compositions_with_query() -> None:
    response = client.get("/search/?q=Brandenburg&type=compositions")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Brandenburg Concerto No. 3" in response.text


def test_composer_detail_page() -> None:
    response = client.get("/composers/1/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Johann Sebastian Bach" in response.text
    assert "Brandenburg Concerto No. 3" in response.text


def test_composer_detail_not_found() -> None:
    response = client.get("/composers/999/")
    assert response.status_code == 404
    assert "text/html" in response.headers["content-type"]
    assert "Composer not found" in response.text


def test_composition_detail_page() -> None:
    response = client.get("/compositions/1/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Brandenburg Concerto No. 3" in response.text
    assert "Johann Sebastian Bach" in response.text
    assert "Concert Hall" in response.text


def test_composition_detail_not_found() -> None:
    response = client.get("/compositions/999/")
    assert response.status_code == 404
    assert "text/html" in response.headers["content-type"]
    assert "Composition not found" in response.text
