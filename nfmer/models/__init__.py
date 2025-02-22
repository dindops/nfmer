from datetime import date
from dataclasses import dataclass, field
from sqlmodel import SQLModel, Field, Relationship
from typing import Dict, Optional, List


@dataclass
class NFM_Event:
    url: str = ""
    event_programme: Dict = field(default_factory=Dict)
    location: str = ""
    date: date = date(9999, 12, 31)
    hour: str = "00:00:00"


class EventBase(SQLModel):
    location: str
    date: date
    hour: str
    url: str


class Event(EventBase, table=True):
    id: str = Field(primary_key=True)
    compositions: List["Composition"] = Relationship(back_populates="event")


class ComposerBase(SQLModel):
    composer_name: str = Field(index=True)


class Composer(ComposerBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    compositions: List["Composition"] = Relationship(back_populates="composer")


class EventCompositionLink(SQLModel, table=True):
    event_id: str = Field(foreign_key="events.id", primary_key=True)
    composition_id: int = Field(foreign_key="compositions.id", primary_key=True)


class CompositionBase(SQLModel):
    composition_name: str = Field(index=True)
    composer_id: int = Field(foreign_key="composers.id")


class Composition(CompositionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    composer: Composer = Relationship(back_populates="compositions")
    events: List["Event"] = Relationship(
        back_populates="compositions",
        link_model=EventCompositionLink
    )


class ComposerPublic(ComposerBase):
    id: int


class CompositionPublic(CompositionBase):
    id: int
    composer: ComposerPublic


class CompositionPublicWithComposers(CompositionPublic):
    composer: ComposerPublic


class ComposerPublicWithCompositions(ComposerPublic):
    compositions: list[CompositionPublic] = []


class EventPublic(EventBase):
    id: str
    compositions: List[CompositionPublic] = []
