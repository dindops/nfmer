from fastapi import APIRouter, Depends, HTTPException

from nfmer.db_handler import DatabaseHandler, get_db
from nfmer.models import EventPublic

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/", response_model=list[str])
def get_events(db: DatabaseHandler = Depends(get_db)) -> list[str]:
    return db.get_all_events()


@router.get("/{event_id}", response_model=EventPublic)
def get_event(event_id: str, db: DatabaseHandler = Depends(get_db)) -> EventPublic:
    event = db.get_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event
