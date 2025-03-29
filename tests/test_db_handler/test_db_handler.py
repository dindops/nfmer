from datetime import date

from sqlmodel import Session

from nfmer.db_handler import DatabaseHandler, get_db
from nfmer.models import NFM_Event


def test_save_and_retrieve_events(db_handler: DatabaseHandler, mock_events_dict: dict[str, NFM_Event]) -> None:
    with Session(db_handler.engine):
        db_handler.save_event_data(mock_events_dict)
        saved_events = db_handler.get_all_events()
        assert len(saved_events) == 2
        composition_by_event = db_handler.get_compositions_by_event("1")
        assert composition_by_event[0].composition_name == "Symphony No. 7"
        composition_by_composer = db_handler.get_compositions_by_composer("Snoop Dogg")
        assert composition_by_composer[0].composition_name == "Gin and Juice"
        all_compositions = db_handler.get_all_compositions()
        assert len(all_compositions) == 2
        gin_and_juice = db_handler.search_compositions_by_name("gin and juice")
        composition2 = db_handler.get_composition_by_id(2)
        assert gin_and_juice[0] == composition2
        all_composers = db_handler.get_all_composers()
        assert len(all_composers) == 2
        snoop_dogg = db_handler.search_composers_by_name("snoop dogg")
        composer2 = db_handler.get_composer_by_id(2)
        assert composer2 == snoop_dogg[0]


def test_update_existing_event(db_handler: DatabaseHandler, mock_events_dict: dict[str, NFM_Event]) -> None:
    db_handler.save_event_data(mock_events_dict)
    event1 = db_handler.get_event_by_id("1")
    assert event1 is not None
    assert event1.location == "Fake place"
    mock_events_dict["1"] = NFM_Event(
        url="https://fake-url.com/events/event/1",
        event_programme={"Kendrick Lamar": "squabble up"},
        location="we outside",
        date=date(2025, 2, 9),
        hour="20:00:00",
    )
    db_handler.save_event_data(mock_events_dict)
    event1 = db_handler.get_event_by_id("1")
    assert event1 is not None
    assert event1.location == "we outside"
    compositions = db_handler.get_compositions_by_event("1")
    assert len(compositions) == 1
    assert compositions[0].composition_name == "squabble up"


def test_get_db() -> None:
    db_generator = get_db()
    db = next(db_generator)
    assert isinstance(db, DatabaseHandler)
