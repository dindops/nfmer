from datetime import date
from nfmer.models import NFM_Event
import pytest
from nfmer.db_handler import DatabaseHandler


@pytest.fixture
def db_handler() -> DatabaseHandler:
    db_handler = DatabaseHandler(db_path="sqlite:///:memory:")
    return db_handler


@pytest.fixture
def mock_events_dict() -> dict[str, NFM_Event]:
    return {
        "1": NFM_Event(
            url="https://fake-url.com/events/event/1",
            event_programme={"A. Dvorak": "Symphony No. 7"},
            location="Fake place",
            date=date(2011, 11, 11),
            hour="19:00:00"
        ),
        "2": NFM_Event(
            url="https://fake-url.com/events/event/2",
            event_programme={"Snoop Dogg": "Gin and Juice"},
            location="Main Hall",
            date=date(2032, 2, 29),
            hour="20:00:00"
        )
    }
