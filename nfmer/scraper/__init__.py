import asyncio
from asyncio import Semaphore
from nfmer.scraper.parser import Parser
from nfmer.scraper.fetcher import Fetcher

NFM_URL = "https://www.nfm.wroclaw.pl/component/nfmcalendar"


class Scraper:
    def __init__(self, fetcher: Fetcher, parser: Parser, max_concurrent: int = 10):
        self.fetcher = fetcher
        self.parser = parser
        self.events_dict = {}
        self.semaphore = Semaphore(max_concurrent)

    @classmethod
    async def initialise(cls, fetcher: Fetcher, parser: Parser):
        scraper = cls(fetcher, parser)
        scraper.events_dict = await scraper._populate_events_dict(NFM_URL)
        return scraper

    async def _populate_events_dict(self, url: str) -> dict[str, str]:
        soup = await self.fetcher.fetch_soup(url)
        events_dict = {}
        for section in soup.find_all("a", class_="nfmEDTitle"):
            href = section["href"]
            event_id = href.split("/")[-1]
            event_url = f"{url}/event/{event_id}"
            events_dict[event_id] = event_url
        return events_dict

    async def _process_single_event(self, event_id: str, event_url: str):
        async with self.semaphore:
            try:
                event_soup = await self.fetcher.fetch_soup(event_url)
                return event_id, self.parser.parse(event_url, event_soup)
            except Exception as e:
                print(f"Skipping {event_id} (URL: {event_url}) due to error: {e}")
                return event_id, None

    async def scrape(self):
        tasks = [
            self._process_single_event(event_id, event_url)
            for event_id, event_url in self.events_dict.items()
        ]
        results = {}
        for event_id, data in await asyncio.gather(*tasks):
            if data is not None:
                results[event_id] = data
        return results


if __name__ == "__main__":
    async def main():
        fetcher = Fetcher()
        parser = Parser()
        scraper = await Scraper.initialise(fetcher, parser)
        return await scraper.scrape()

    print(asyncio.run(main()))


# TODO: confirm if this really retrieves all events
# TODO: perhaps the output should be in a json format, and not a dictionary?
