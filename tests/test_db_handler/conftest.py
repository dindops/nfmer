from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session, declarative_base
from datetime import date
from nfmer.db_handler import DatabaseHandler
from nfmer.models import NFM_Event
import pytest


@pytest.fixture
def db_engine() -> Engine:
    Base = declarative_base()
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(db_engine) -> Session:
    with Session(db_engine) as session:
        yield session
        session.rollback()


@pytest.fixture
def db_handler(db_engine) -> DatabaseHandler:
    return DatabaseHandler(db_path="sqlite:///:memory:")


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
