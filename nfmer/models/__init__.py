from dataclasses import dataclass, field
from datetime import date
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


@dataclass
class NFM_Event:
    url: str = ""
    event_programme: dict = field(default_factory=dict)
    location: str = ""
    date: date = date(9999, 12, 31)
    hour: str = "00:00:00"


class EventBase(SQLModel):
    location: str
    date: date
    hour: str
    url: str


class EventCompositionLink(SQLModel, table=True):
    __tablename__ = "event_composition_link"
    event_id: str = Field(foreign_key="events.id", primary_key=True)
    composition_id: int = Field(foreign_key="compositions.id", primary_key=True)


class EventPublic(EventBase):
    id: str


class Event(EventBase, table=True):
    __tablename__ = "events"
    id: str = Field(primary_key=True)
    compositions: list["Composition"] = Relationship(
        back_populates="events",
        link_model=EventCompositionLink,
        sa_relationship_kwargs={"secondary": "event_composition_link"},
    )


class ComposerBase(SQLModel):
    composer_name: str = Field(index=True)


class Composer(ComposerBase, table=True):
    __tablename__ = "composers"
    id: Optional[int] = Field(default=None, primary_key=True)
    compositions: list["Composition"] = Relationship(back_populates="composer")


class CompositionBase(SQLModel):
    composition_name: str = Field(index=True)


class Composition(CompositionBase, table=True):
    __tablename__ = "compositions"
    id: Optional[int] = Field(default=None, primary_key=True)
    composer_id: int = Field(foreign_key="composers.id")
    composer: Composer = Relationship(back_populates="compositions")
    events: list["Event"] = Relationship(
        back_populates="compositions",
        link_model=EventCompositionLink,
        sa_relationship_kwargs={"secondary": "event_composition_link"},
    )


class ComposerPublic(ComposerBase):
    compostions: list[Composition]


class CompositionPublic(CompositionBase):
    id: int


class CompositionPublicWithComposer(CompositionPublic):
    composer: ComposerBase


class CompositionPublicFull(CompositionPublic):
    composer: ComposerBase
    events: list[EventPublic]


class ComposerPublicWithCompositions(ComposerPublic):
    compositions: list[CompositionPublicFull] = []
