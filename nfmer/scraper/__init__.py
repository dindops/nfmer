import asyncio
from asyncio import Semaphore
from nfmer.scraper.parser import Parser
from nfmer.scraper.fetcher import Fetcher, FetcherException
from nfmer.models import NFM_Event
from nfmer.db_handler import DatabaseHandler

NFM_URL = "https://www.nfm.wroclaw.pl/component/nfmcalendar"


class ScraperException(Exception):
    pass


class Scraper:
    def __init__(
        self,
        fetcher: Fetcher,
        parser: Parser,
        main_url: str,
        max_concurrent: int = 10
    ):
        self.fetcher = fetcher
        self.parser = parser
        self.main_url = main_url
        self.events_dict = {}
        self.semaphore = Semaphore(max_concurrent)

    @classmethod
    async def initialise(cls, fetcher: Fetcher, parser: Parser, main_url: str = NFM_URL):
        scraper = cls(fetcher, parser, main_url)
        scraper.events_dict = await scraper._populate_events_dict()
        return scraper

    async def _populate_events_dict(self) -> dict[str, str]:
        url = self.main_url
        try:
            soup = await self.fetcher.fetch_soup(url)
        except FetcherException as e:
            raise ScraperException("Couldn't gather a list of events urls to parse through.",
                                   f"\nDetails: {e}")
        events_dict = {}
        for section in soup.find_all("a", class_="nfmEDTitle"):
            href = section["href"]
            event_id = href.split("/")[-1]
            event_url = f"{url}/event/{event_id}"
            events_dict[event_id] = event_url
        return events_dict

    async def _process_single_event(self, event_id: str, event_url: str) -> tuple[str, NFM_Event | None]:
        async with self.semaphore:
            try:
                event_soup = await self.fetcher.fetch_soup(event_url)
                return event_id, self.parser.parse(event_url, event_soup)
            except FetcherException:
                return event_id, None
            except Exception as e:
                print(f"Skipping {event_id} (URL: {event_url}) due to an error: {e}")
                return event_id, None

    async def scrape(self) -> dict[str, NFM_Event]:
        tasks = [
            self._process_single_event(event_id, event_url)
            for event_id, event_url in self.events_dict.items()
        ]
        results = {}
        for event_id, data in await asyncio.gather(*tasks):
            if data is not None:
                results[event_id] = data
        return results


async def run_scraper() -> None:
    fetcher = Fetcher()
    parser = Parser()
    scraper = await Scraper.initialise(fetcher, parser)
    scraped_events = await scraper.scrape()
    db_handler = DatabaseHandler()
    db_handler.save_event_data(scraped_events)


def main() -> None:
    asyncio.run(run_scraper())
