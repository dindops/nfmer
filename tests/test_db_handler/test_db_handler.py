from nfmer.db_handler import DatabaseHandler
from nfmer.models import NFM_Event
from datetime import date
from sqlmodel import Session


def test_save_new_event(db_handler: DatabaseHandler,
                        mock_events_dict: dict[str, NFM_Event]) -> None:
    with Session(db_handler.engine):
        db_handler.save_event_data(mock_events_dict)
        saved_events = db_handler.get_all_events()
        assert len(saved_events) == 2
        composition_by_event = db_handler.get_compositions_by_event(1)
        assert composition_by_event[0].composition_name == "Symphony No. 7"
        composition_by_composer = db_handler.get_compositions_by_composer("Snoop Dogg")
        assert composition_by_composer[0].composition_name == "Gin and Juice"


def test_update_existing_event(db_handler: DatabaseHandler,
                               mock_events_dict: dict[str, NFM_Event]) -> None:
    db_handler.save_event_data(mock_events_dict)
    event1 = db_handler.get_event_by_id("1")
    assert event1.location == "Fake place"
    mock_events_dict["1"] = NFM_Event(
        url="https://fake-url.com/events/event/1",
        event_programme={"Kendrick Lamar": "squabble up"},
        location="we outside",
        date=date(2025, 2, 9),
        hour="20:00:00"
    )
    db_handler.save_event_data(mock_events_dict)
    event1 = db_handler.get_event_by_id("1")
    assert event1.location == "we outside"
    compositions = db_handler.get_compositions_by_event("1")
    assert len(compositions) == 1
    assert compositions[0].composition_name == "squabble up"
