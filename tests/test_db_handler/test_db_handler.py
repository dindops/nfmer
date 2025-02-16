from nfmer.db_handler import DatabaseHandler
from nfmer.models import NFM_Event
from datetime import date


def test_save_new_event(db_handler: DatabaseHandler,
                        mock_events_dict: dict[str, NFM_Event]) -> None:
    db_handler.save_event_data(mock_events_dict)
    saved_events = db_handler.get_all_events()
    assert len(saved_events) == 2
    event1 = db_handler.get_event_by_id("1")
    assert event1.location == "Fake place"
    assert event1.date == date(2011, 11, 11)
    artists1 = db_handler.get_artists_by_event("1")
    assert len(artists1) == 1
    assert artists1[0].artist_name == "A. Dvorak"
    assert artists1[0].song_name == "Symphony No. 7"


def test_update_existing_event(db_handler: DatabaseHandler,
                               mock_events_dict: dict[str, NFM_Event]) -> None:
    db_handler.save_event_data(mock_events_dict)
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
    artists1 = db_handler.get_artists_by_event("1")
    assert len(artists1) == 1
    assert artists1[0].artist_name == "Kendrick Lamar"
    assert artists1[0].song_name == "squabble up"
