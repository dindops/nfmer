from typing import List

from fastapi import APIRouter, Depends, HTTPException

from nfmer.db_handler import DatabaseHandler, get_db
from nfmer.models import CompositionPublicWithComposers, EventPublic

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/", response_model=List[EventPublic])
def get_events(db: DatabaseHandler = Depends(get_db)) -> List[EventPublic]:
    return db.get_all_events()


@router.get("/{event_id}", response_model=EventPublic)
def get_event(event_id: str, db: DatabaseHandler = Depends(get_db)) -> EventPublic:
    event = db.get_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.get(
    "/{event_id}/compositions", response_model=List[CompositionPublicWithComposers]
)
def get_event_compositions(
    event_id: str, db: DatabaseHandler = Depends(get_db)
) -> List[CompositionPublicWithComposers]:
    compositions = db.get_compositions_by_event(event_id)
    if not compositions:
        raise HTTPException(status_code=404, detail="Event or compositions not found")
    return compositions
