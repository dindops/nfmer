#!/usr/bin/env python

import sqlite3
from scraper import Scraper, retrieve_events_urls
import asyncio


DB_FILE = "nfm_events.db"
NFM_URL = "https://www.nfm.wroclaw.pl/component/nfmcalendar"

class ScraperDBHandler:
    def __init__(self, events_list: list):
        __db_location = "nfm_events.db"
        self.events_list = events_list
        self.conn = sqlite3.connect(__db_location)
        self._initialize_database()
        self.existing_events_ids = self._get_list_of_event_ids()

    def __exit__(self, exc_value):
        if isinstance(exc_value, Exception):
            self.conn.rollback()
        else:
            self.conn.commit()
        self.conn.close()

    def _initialize_database(self) -> None:
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS nfm_events (
                event_id INTEGER PRIMARY KEY,
                url TEXT,
                event_programme TEXT,
                location TEXT,
                date TEXT
            )
        ''')
        self.conn.commit()

    def _get_list_of_event_ids(self) -> set:
        cursor = self.conn.cursor()
        cursor.execute('SELECT event_id FROM nfm_events')
        rows = cursor.fetchall()
        event_ids = {row[0] for row in rows}
        return event_ids


    def _insert_event_data(self, event):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO nfm_events (event_id, url, event_programme, location, date)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            event.event_id,
            event.url,
            str(event.event_programme),
            event.location,
            event.date
        ))
        self.conn.commit()

    def _update_event_data(self, event):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE nfm_events
            SET url = ?, event_programme = ?, location = ?, date = ?
            WHERE event_id = ?
        ''', (
            event.url,
            str(event.event_programme),  # Convert dictionary to string
            event.location,
            event.date,
            event.event_id
        ))
        self.conn.commit()

    def save_events_to_db(self) -> None:
        for event in self.events_list:
            if event.event_id in self.existing_events_ids:
                self._update_event_data(event)
            else:
                self._insert_event_data(event)
        self.conn.close()


async def main():
    nfm_events_urls = [
            # "https://www.nfm.wroclaw.pl/component/nfmcalendar/event/10060",
            # "https://www.nfm.wroclaw.pl/component/nfmcalendar/event/10164",
            # "https://www.nfm.wroclaw.pl/component/nfmcalendar/event/10102"
            "https://www.nfm.wroclaw.pl/component/nfmcalendar/event/10346"
            ]
    scraper = Scraper(*nfm_events_urls)
    await scraper.scrape()
    nfm_events = scraper.event_soup
    db_handler = ScraperDBHandler(nfm_events)
    db_handler.save_events_to_db()

    # TODO:
    # * update procedure:
    #   * check if event data is being updated correctly  DONE
    #   * behavioral class?
    # * move execution to scraper.py

if __name__ == "__main__":
    asyncio.run(main())

