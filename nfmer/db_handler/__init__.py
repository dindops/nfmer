from typing import Dict, Optional

from sqlmodel import Session, SQLModel, create_engine, select

from nfmer.models import (Composer, Composition,
                          CompositionPublicWithComposers, Event,
                          EventCompositionLink, NFM_Event)


class DatabaseHandler:
    def __init__(self, db_path: str = "sqlite:///events.db"):
        self.engine = create_engine(db_path)
        SQLModel.metadata.create_all(self.engine)

    def _handle_event_table(
        self, session: Session, event_id: str, event_data: NFM_Event
    ) -> Event:
        event = session.get(Event, event_id)
        if event:
            event = self._update_event(event, event_data)
        else:
            event = self._create_event(event_id, event_data)
            session.add(event)
        return event

    def _update_event(self, event: Event, event_data: NFM_Event) -> Event:
        event.location = event_data.location
        event.date = event_data.date
        event.hour = event_data.hour
        event.url = event_data.url
        return event

    def _create_event(self, event_id: str, event_data: NFM_Event) -> Event:
        return Event(
            id=event_id,
            location=event_data.location,
            date=event_data.date,
            hour=event_data.hour,
            url=event_data.url,
        )

    def _handle_composer_table(self, session: Session, composer_name: str) -> Composer:
        composer = session.exec(
            select(Composer).where(Composer.composer_name == composer_name)
        ).first()
        if not composer:
            composer = Composer(composer_name=composer_name)
            session.add(composer)
            session.flush()  # Required get the composer.id in the middle of the transaction
        return composer

    def _handle_composition_table(
        self, session: Session, composition_name: str, composer: Composer
    ) -> Composition:
        composition = session.exec(
            select(Composition)
            .where(Composition.composition_name == composition_name)
            .where(Composition.composer_id == composer.id)
        ).first()
        if not composition:
            composition = Composition(
                composition_name=composition_name, composer=composer
            )
            session.add(composition)
        return composition

    def _clear_event_compositions(self, session: Session, event_id: str) -> None:
        statement = (
            select(Composition)
            .join(EventCompositionLink)
            .where(EventCompositionLink.event_id == event_id)
        )
        event_compositions = session.exec(statement).first()
        if event_compositions:
            session.delete(event_compositions)
            session.commit()

    def save_event_data(self, parsed_results: Dict[str, NFM_Event]) -> None:
        with Session(self.engine) as session:
            for event_id, event_data in parsed_results.items():
                event = self._handle_event_table(session, event_id, event_data)
                self._clear_event_compositions(session, event_id)

                if event_data.event_programme:
                    for (
                        composer_name,
                        composition_name,
                    ) in event_data.event_programme.items():
                        composer = self._handle_composer_table(session, composer_name)
                        composition = self._handle_composition_table(
                            session, composition_name, composer
                        )
                        event.compositions.append(composition)
            session.commit()

    def get_all_events(self) -> list[Event]:
        with Session(self.engine) as session:
            return session.exec(select(Event)).all()

    def get_event_by_id(self, event_id: str) -> Optional[Event]:
        with Session(self.engine) as session:
            return session.get(Event, event_id)

    def get_compositions_by_event(
        self, event_id: str
    ) -> list[CompositionPublicWithComposers]:
        with Session(self.engine) as session:
            event = session.get(Event, event_id)
            if not event:
                return []
            for composition in event.compositions:
                _ = composition.composer  # This triggers loading of the composer
            return event.compositions

    def get_compositions_by_composer(self, composer_name: str) -> list[Composition]:
        with Session(self.engine) as session:
            return session.exec(
                select(Composition)
                .join(Composer)
                .where(Composer.composer_name == composer_name)
            ).all()


def get_db():
    db = DatabaseHandler()
    try:
        yield db
    finally:
        pass
