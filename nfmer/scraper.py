#!/usr/bin/env python

from typing import Dict
import requests
from bs4 import BeautifulSoup, Tag, NavigableString
from datetime import datetime
import httpx
import asyncio

NFM_URL = "https://www.nfm.wroclaw.pl/component/nfmcalendar"

class Scraper:
    ''' Gets URL (or list of URLS), crawls over them and returns a dictionary,
    with url as key and bs4.soup as a value '''
    def __init__(self, *urls) -> None:
        self.urls = urls
        self.soup = {}
        self.todo = []

    async def _fetch_soup(self, url):
        async with httpx.AsyncClient() as client:
            await asyncio.sleep(5)  # pseudo rate-limiting
            response = await client.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            self.soup[url] = soup

    async def main(self):
        for url in self.urls:
            task = asyncio.create_task(self._fetch_soup(url))
            self.todo.append(task)
        results = await asyncio.gather(*self.todo, return_exceptions=True)
        for url, result in zip(self.urls, results):
            if isinstance(result, httpx.TimeoutException):
                print(f"Timeout for event {url}")
                continue

    async def scrape(self):
        await self.main()

    @property
    def event_soup(self):
        return self.soup

def retrieve_events_urls(url) -> list:
    response = httpx.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    events_urls = []
    for section in soup.find_all("a", class_="nfmEDTitle"):
        href = section["href"]
        event_id = href.split("/")[-1]
        event_url = f"{url}/event/{event_id}"
        events_urls.append(event_url)
    return events_urls



def format_progamme_section(programme_section) -> dict:
    all_p_tags = programme_section.find_next_siblings('p')
    tag_list = programme_section.contents
    for p_tag in all_p_tags:
        tag_list += p_tag.contents
    programme_dict = {}
    current_key = None
    current_value = []
    for item in tag_list:
        # shenanigans to distinguish composer from their work included within
        # few <p> tags
        if isinstance(item, Tag) and item.name == 'strong':
            if "<img " in item.text:
                continue
            if "Mecenas Edukacji NFM" in item.text:
                continue
            # TODO: - all ^^^ those weird entries in <p> tags should be handled
            # in a separate function
            if current_key is not None:
                if '***' in current_value:  # *** is used as a break indicator
                    current_value.remove('***')
                programme_dict[current_key] = ''.join(current_value)
            current_key = item.text
            current_value = []
            # TODO: get rid of all those \xa0 characters in programme (i.e. event 9877)
        else:
            current_value.append(item.text)
        if current_key is not None and current_key != '':
            programme_dict[current_key] = ''.join(current_value)
    return programme_dict


def format_artists_section(artists_section) -> str:
    # not gonna work on this too much, as might have to remove it in the end
    artists = ''
    for item in artists_section.contents:
        if type(item) is not Tag:
            artists += item + ', '
    artists = artists[:-2]
    return artists


def retrieve_event_date(soup) -> str:
    # TODO currently dates don't come with a year - how to figure out from
    # which year an event is exactly? From tickets info, but this require
    # further crawling
    event_date_raw = soup.find('div', class_="nfmEDDate nfmComEvDate")
    try:
        event_date_list = event_date_raw.text.strip().split(".")
        event_date = f"{datetime.now().year}-{event_date_list[1]}-" \
            f"{event_date_list[0]}"
    except AttributeError:
        event_date = "TBD"
    return event_date


def retrieve_event_hour(soup) -> str:
    event_hour_raw = soup.find('div', class_="nfmEDTime nfmComEvTime")
    try:
        event_hour = event_hour_raw.text.strip()
        event_hour = f"{event_hour}:00"
    except AttributeError:
        event_hour = "00:00:00"
    return event_hour


def retrieve_data_about_all_events(events: dict) -> dict:
    for event in events.keys():
        event_url = events[event]["url"]
        response = requests.get(event_url)
        soup = BeautifulSoup(response.content, "html.parser")
        program = retrieve_event_data(soup, "program")
        location = retrieve_event_data(soup, "lokalizacja")
        performers = retrieve_event_data(soup, "wykonawcy")
        date = retrieve_event_date(soup)
        hour = retrieve_event_hour(soup)
        date_8601 = f"{date} {hour}"
        events[event]["program"] = program
        events[event]["performers"] = performers
        events[event]["location"] = location
        events[event]["date"] = date_8601
    return events


async def main():
    nfm_events_urls = retrieve_events_urls(NFM_URL)
    scraper = Scraper(*nfm_events_urls)
    await scraper.scrape()
    nfm_events = scraper.event_soup
    print(nfm_events)

if __name__ == "__main__":
    asyncio.run(main())



"""
TODO:
* confirm if this really retrieves all events
* figure out data classes for each entry/event
* perhaps the output should be in a json format?
"""
