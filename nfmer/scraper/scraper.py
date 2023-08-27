#!/usr/bin/env python

from typing import Dict
from bs4 import BeautifulSoup
from parser import Parser
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

    async def _fetch_soup(self, url) -> None:
        async with httpx.AsyncClient() as client:
            await asyncio.sleep(10)  # pseudo rate-limiting
            response = await client.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            parser = Parser(soup)
            parser.parse()
            parsed_soup = parser.get_parsed_event
            self.soup[url] = parsed_soup

    async def main(self) -> None:
        for url in self.urls:
            task = asyncio.create_task(self._fetch_soup(url))
            self.todo.append(task)
        results = await asyncio.gather(*self.todo, return_exceptions=True)
        for url, result in zip(self.urls, results):
            if isinstance(result, httpx.TimeoutException):
                print(f"Timeout for event {url}")  # TODO: add logger
                continue

    async def scrape(self) -> None:
        await self.main()

    @property
    def event_soup(self) -> Dict:
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
