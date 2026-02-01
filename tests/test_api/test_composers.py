import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from nfmer.api.v1.api import api
from nfmer.models import Composer, Composition
from nfmer.db_handler import DatabaseHandler, get_db

client = TestClient(api)

mock_composers = [
    Composer(id=1, composer_name="Johann Sebastian Bach", compositions=[]),
    Composer(id=2, composer_name="Wolfgang Amadeus Mozart", compositions=[]),
]

mock_compositions = [
    Composition(id=1, composition_name="Brandenburg Concerto No. 3", composer_id=1),
    Composition(id=2, composition_name="Symphony No. 40", composer_id=2),
]


@pytest.fixture
def mock_db(mocker: MockerFixture):
    db = mocker.MagicMock(spec=DatabaseHandler)
    db.get_all_composers.return_value = mock_composers
    db.search_composers_by_name.return_value = [mock_composers[0]]
    bach_with_compositions = Composer(
        id=1,
        composer_name="Johann Sebastian Bach",
        compositions=[mock_compositions[0]]
    )
    db.get_composer_by_id.side_effect = lambda id: (
        bach_with_compositions if id == 1
        else mock_composers[1] if id == 2
        else None
    )
    return db


@pytest.fixture(autouse=True)
def override_dependency(mock_db):
    api.dependency_overrides[get_db] = lambda: mock_db
    yield
    api.dependency_overrides = {}


def test_get_all_composers():
    response = client.get("/composers/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["composer_name"] == "Johann Sebastian Bach"
    assert data[1]["composer_name"] == "Wolfgang Amadeus Mozart"


def test_search_composers():
    response = client.get("/composers/?search=Bach")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["composer_name"] == "Johann Sebastian Bach"


def test_get_composer_by_id():
    response = client.get("/composers/1")
    assert response.status_code == 200
    data = response.json()
    assert data["composer_name"] == "Johann Sebastian Bach"
    assert "compositions" in data
    assert len(data["compositions"]) == 1
    assert data["compositions"][0]["composition_name"] == "Brandenburg Concerto No. 3"


def test_get_composer_not_found():
    response = client.get("/composers/999")  # ID that doesn't exist
    assert response.status_code == 404
    assert response.json()["detail"] == "Composer not found"
