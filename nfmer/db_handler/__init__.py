from typing import Dict, Optional

from sqlalchemy.orm import selectinload
from sqlmodel import Session, SQLModel, create_engine, select

from nfmer.models import (Composer, ComposerPublic, ComposerPublicFull,
                          Composition, CompositionPublic,
                          CompositionPublicFull, Event, EventCompositionLink,
                          EventPublic, NFM_Event)


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

    def get_all_events(self) -> list[str]:
        with Session(self.engine) as session:
            return session.exec(select(Event.id)).all()

    def get_event_by_id(self, event_id: str) -> Optional[EventPublic]:
        with Session(self.engine) as session:
            return session.get(Event, event_id)

    def get_all_compositions(self) -> list[CompositionPublic]:
        with Session(self.engine) as session:
            return session.exec(select(Composition)).all()

    def search_compositions_by_name(self, search_term: str) -> list[CompositionPublic]:
        with Session(self.engine) as session:
            query = (
                select(Composition)
                .where(Composition.composition_name.like(f"%{search_term}%"))
                .options(
                    selectinload(Composition.composer), selectinload(Composition.events)
                )
            )
            return session.exec(query).all()

    def get_composition_by_id(
        self, composition_id: int
    ) -> Optional[CompositionPublicFull]:
        with Session(self.engine) as session:
            statement = (
                select(Composition)
                .where(Composition.id == composition_id)
                .options(
                    selectinload(Composition.composer), selectinload(Composition.events)
                )
            )
            return session.exec(statement).first()

    def get_all_composers(self) -> list[ComposerPublic]:
        with Session(self.engine) as session:
            return session.exec(select(Composer)).all()

    def search_composers_by_name(self, search_term: str) -> list[ComposerPublic]:
        with Session(self.engine) as session:
            query = select(Composer).where(
                Composer.composer_name.like(f"%{search_term}%")
            )
            return session.exec(query).all()

    def get_composer_by_id(self, composer_id: int) -> Optional[ComposerPublicFull]:
        with Session(self.engine) as session:
            statement = (
                select(Composer)
                .where(Composer.id == composer_id)
                .options(
                    selectinload(Composer.compositions).selectinload(
                        Composition.events
                    ),
                    selectinload(Composer.compositions).selectinload(
                        Composition.composer
                    ),
                )
            )
            return session.exec(statement).first()

    def get_compositions_by_event(self, event_id: str) -> list[CompositionPublic]:
        with Session(self.engine) as session:
            statement = (
                select(Composition)
                .join(EventCompositionLink)
                .where(EventCompositionLink.event_id == event_id)
                .options(
                    selectinload(Composition.composer), selectinload(Composition.events)
                )
            )
            return session.exec(statement).all()

    def get_compositions_by_composer(self, composer_name: str) -> list[Composition]:
        with Session(self.engine) as session:
            return session.exec(
                select(Composition)
                .join(Composer)
                .where(Composer.composer_name == composer_name)
                .options(
                    selectinload(Composition.composer), selectinload(Composition.events)
                )
            ).all()


def get_db():
    db = DatabaseHandler()
    try:
        yield db
    finally:
        pass
