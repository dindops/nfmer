#!/usr/bin/env python

import sqlite3
from scraper import Scraper, retrieve_events_urls
import asyncio


DB_FILE = "nfm_events.db"
NFM_URL = "https://www.nfm.wroclaw.pl/component/nfmcalendar"

def initialize_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nfm_events (
            event_id INTEGER PRIMARY KEY,
            url TEXT,
            event_programme TEXT,
            location TEXT,
            date TEXT
        )
    ''')

    conn.commit()
    conn.close()


def get_list_of_event_ids() -> set:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT event_id FROM nfm_events')
    rows = cursor.fetchall()
    event_ids = {row[0] for row in rows}
    conn.close()
    return event_ids


def insert_event_data(event):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

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

    conn.commit()
    conn.close()

def update_event_data(event):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
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
    conn.commit()
    conn.close()


def handle_saving_events_to_db(events_list) -> None:
    existing_event_ids = get_list_of_event_ids()
    for event in events_list:
        if event.event_id in existing_event_ids:
            update_event_data(event)
        else:
            insert_event_data(event)


async def main():
    scraper = Scraper(NFM_URL)
    await scraper.scrape()
    nfm_events = scraper.event_soup
    initialize_database()
    handle_saving_events_to_db(nfm_events)

if __name__ == "__main__":
    asyncio.run(main())

