from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship, Session, declarative_base
from typing import Dict
from nfmer.models import NFM_Event

Base = declarative_base()


class Event(Base):
    __tablename__ = 'events'

    event_id = Column(String, primary_key=True)
    location = Column(String)
    date = Column(Date)
    hour = Column(String)
    url = Column(String)

    artists = relationship("Artist", back_populates="event")


class Artist(Base):
    __tablename__ = 'artists'

    song_id = Column(Integer, primary_key=True, autoincrement=True)
    artist_name = Column(String)
    song_name = Column(String)
    event_id = Column(String, ForeignKey('events.event_id'))

    event = relationship("Event", back_populates="artists")


class DatabaseHandler:
    def __init__(self, db_path: str = 'sqlite:///events.db'):
        self.engine = create_engine(db_path)
        Base.metadata.create_all(self.engine)

    def save_event_data(self, parsed_results: Dict[str, NFM_Event]) -> None:
        with Session(self.engine) as session:
            for event_id, event_data in parsed_results.items():
                existing_event = session.query(Event).filter(Event.event_id == event_id).first()
                if existing_event:
                    existing_event.location = event_data.location
                    existing_event.date = event_data.date
                    existing_event.hour = event_data.hour
                    existing_event.url = event_data.url
                    session.query(Artist).filter(Artist.event_id == event_id).delete()
                    event = existing_event
                else:
                    event = Event(
                        event_id=event_id,
                        location=event_data.location,
                        date=event_data.date,
                        hour=event_data.hour,
                        url=event_data.url
                    )
                    session.add(event)
                if event_data.event_programme:  # event_programme is empty at early date
                    for composer, works in event_data.event_programme.items():
                        artist = Artist(
                            artist_name=composer,
                            song_name=works,
                            event=event
                        )
                        session.add(artist)
            session.commit()

    def get_all_events(self) -> list[Event]:
        with Session(self.engine) as session:
            return session.query(Event).all()

    def get_event_by_id(self, event_id: str) -> Event:
        with Session(self.engine) as session:
            return session.query(Event).filter(Event.event_id == event_id).first()

    def get_artists_by_event(self, event_id: str) -> list[Artist]:
        with Session(self.engine) as session:
            return session.query(Artist).filter(Artist.event_id == event_id).all()
